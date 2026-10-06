from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Response
from sqlmodel import Session, or_, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.models import Duel, Exercise, User
from backend.queries import group_records
from backend.routes.rankings import GroupContext, context, r1
from backend.schemas import DuelInput, DuelOut, Person, SuggestionOut, SuggestionsOut

router = APIRouter(prefix="/api")


def person(ctx: GroupContext, user_id: int) -> Person:
    user = ctx.users.get(user_id)
    return Person(user_id=user_id, display_name=user.display_name if user else "ex miembro")


def sexes_for(session: Session, ctx: GroupContext, *user_ids: int) -> dict[int, str]:
    sexes = {uid: u.sex for uid, u in ctx.users.items()}
    for uid in user_ids:
        if uid not in sexes:
            sexes[uid] = session.get(User, uid).sex
    return sexes


def duel_out(session: Session, ctx: GroupContext, duel: Duel, records: list[stats.SetRecord]) -> DuelOut:
    exercise = session.get(Exercise, duel.exercise_id)
    base = dict(id=duel.id, challenger=person(ctx, duel.challenger_id), opponent=person(ctx, duel.opponent_id),
                exercise=exercise.name, exercise_id=exercise.id, mode=duel.mode, days=duel.days, start=duel.start)
    if duel.status != "active":
        return DuelOut(**base, status=duel.status, end=None, challenger_value=None, opponent_value=None, winner_id=None)
    result = stats.duel_result(records, sexes_for(session, ctx, duel.challenger_id, duel.opponent_id),
                               duel.challenger_id, duel.opponent_id, duel.exercise_id, duel.mode, duel.start, duel.days,
                               date.today())
    return DuelOut(**base, status="finished" if result.finished else "active", end=result.end,
                   challenger_value=r1(result.challenger_value), opponent_value=r1(result.opponent_value),
                   winner_id=result.winner)


@router.get("/groups/{code}/duels", response_model=list[DuelOut])
def list_duels(code: str, user: UserDep, session: SessionDep) -> list[DuelOut]:
    ctx = context(session, code, user)
    duels = list(session.exec(select(Duel).where(Duel.group_id == ctx.group.id).order_by(Duel.id.desc())))
    involved = {uid for d in duels for uid in (d.challenger_id, d.opponent_id)}
    records = group_records(session, ctx.group.id, sorted(involved | set(ctx.ids)))
    return [duel_out(session, ctx, d, records) for d in duels]


def month_bests(ctx: GroupContext, records: list[stats.SetRecord], exercise_id: int, mode: str) -> dict[int, float]:
    today = date.today()
    window = stats.in_range(records, stats.month_start(today), stats.month_end(today))
    table = stats.strength_table(window, {uid: u.sex for uid, u in ctx.users.items()}, exercise_id, mode)
    return {e.user_id: e.value for e in table if e.value is not None}


@router.get("/groups/{code}/duels/suggestions", response_model=SuggestionsOut)
def suggestions(code: str, exercise_id: int, mode: str, user: UserDep, session: SessionDep) -> SuggestionsOut:
    if mode not in ("absolute", "dots"):
        raise HTTPException(status_code=422, detail="El modo es 'absolute' o 'dots'")
    ctx = context(session, code, user)
    bests = month_bests(ctx, group_records(session, ctx.group.id, ctx.ids), exercise_id, mode)
    mine = bests.get(user.id)
    rivals = []
    for uid in ctx.ids:
        if uid == user.id:
            continue
        level, ratio = stats.imbalance(mine, bests.get(uid))
        rivals.append(SuggestionOut(user_id=uid, display_name=ctx.name(uid), value=r1(bests.get(uid)), level=level,
                                    ratio=ratio))
    rivals.sort(key=lambda s: (s.ratio is None, s.ratio or 0, s.display_name))
    return SuggestionsOut(mine=r1(mine), rivals=rivals)


def open_duel_between(session: Session, group_id: int, a: int, b: int) -> Duel | None:
    pair = or_((Duel.challenger_id == a) & (Duel.opponent_id == b), (Duel.challenger_id == b) & (Duel.opponent_id == a))
    for duel in session.exec(select(Duel).where(Duel.group_id == group_id, pair, Duel.status.in_(["pending", "active"]))):
        if duel.status == "pending" or date.today() < duel.start + timedelta(days=duel.days):
            return duel
    return None


@router.post("/groups/{code}/duels", response_model=DuelOut, status_code=201)
def create_duel(code: str, data: DuelInput, user: UserDep, session: SessionDep) -> DuelOut:
    ctx = context(session, code, user)
    if data.opponent_id == user.id:
        raise HTTPException(status_code=422, detail="No te podés retar a vos mismo")
    if data.opponent_id not in ctx.users:
        raise HTTPException(status_code=422, detail="Ese rival no es miembro del grupo")
    if session.get(Exercise, data.exercise_id) is None:
        raise HTTPException(status_code=422, detail="Ese ejercicio no existe")
    if open_duel_between(session, ctx.group.id, user.id, data.opponent_id):
        raise HTTPException(status_code=409, detail="Ya tienen un duelo pendiente o en curso")
    duel = Duel(group_id=ctx.group.id, challenger_id=user.id, **data.model_dump())
    session.add(duel)
    session.commit()
    session.refresh(duel)
    return duel_out(session, ctx, duel, [])


def answer(session: Session, code: str, duel_id: int, user: User, accept: bool) -> DuelOut:
    ctx = context(session, code, user)
    duel = session.get(Duel, duel_id)
    if duel is None or duel.group_id != ctx.group.id:
        raise HTTPException(status_code=404, detail="Ese duelo no existe")
    if duel.opponent_id != user.id:
        raise HTTPException(status_code=403, detail="Solo el retado puede responder")
    if duel.status != "pending":
        raise HTTPException(status_code=409, detail="Ese duelo ya fue respondido")
    duel.status = "active" if accept else "rejected"
    duel.start = date.today() if accept else None
    session.commit()
    session.refresh(duel)
    return duel_out(session, ctx, duel, group_records(session, ctx.group.id, ctx.ids))


@router.post("/groups/{code}/duels/{duel_id}/accept", response_model=DuelOut)
def accept_duel(code: str, duel_id: int, user: UserDep, session: SessionDep) -> DuelOut:
    return answer(session, code, duel_id, user, accept=True)


@router.post("/groups/{code}/duels/{duel_id}/reject", response_model=DuelOut)
def reject_duel(code: str, duel_id: int, user: UserDep, session: SessionDep) -> DuelOut:
    return answer(session, code, duel_id, user, accept=False)


@router.delete("/groups/{code}/duels/{duel_id}", status_code=204)
def cancel_duel(code: str, duel_id: int, user: UserDep, session: SessionDep) -> Response:
    ctx = context(session, code, user)
    duel = session.get(Duel, duel_id)
    if duel is None or duel.group_id != ctx.group.id:
        raise HTTPException(status_code=404, detail="Ese duelo no existe")
    if duel.challenger_id != user.id:
        raise HTTPException(status_code=403, detail="Solo quien retó puede cancelar")
    if duel.status != "pending":
        raise HTTPException(status_code=409, detail="Solo se cancela un reto que todavía no fue aceptado")
    session.delete(duel)
    session.commit()
    return Response(status_code=204)

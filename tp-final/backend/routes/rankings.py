from dataclasses import dataclass
from datetime import date

from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import Session, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.groups import challenge_exercises, members_with_users, require_member
from backend.models import Exercise, Group, Reaction, User
from backend.queries import excluded_sets, goal_changes, group_records, set_records
from backend.schemas import (
    ConsistencyRow, FeedItem, PeriodOut, ProgressRow, RankingsOut, ReactionInput, StrengthExercise, StrengthRow,
    WeeklyRow,
)

router = APIRouter(prefix="/api")


@dataclass
class GroupContext:
    group: Group
    users: dict[int, User]

    @property
    def ids(self) -> list[int]:
        return list(self.users)

    def name(self, user_id: int) -> str:
        return self.users[user_id].display_name


def context(session: Session, code: str, user: User) -> GroupContext:
    group, _ = require_member(session, code, user)
    return GroupContext(group, {u.id: u for _m, u in members_with_users(session, group)})


def r1(value: float | None) -> float | None:
    return None if value is None else round(value, 1)


def strength_rows(ctx: GroupContext, entries: list[stats.StrengthEntry]) -> list[StrengthRow]:
    return [StrengthRow(user_id=e.user_id, display_name=ctx.name(e.user_id), value=r1(e.value),
                        weight_kg=e.weight_kg, reps=e.reps) for e in entries]


@router.get("/groups/{code}/rankings", response_model=RankingsOut)
def rankings(code: str, user: UserDep, session: SessionDep, period: str = "month", month: str | None = None,
             start: str | None = Query(None, alias="from"), end: str | None = Query(None, alias="to")) -> RankingsOut:
    ctx = context(session, code, user)
    records = group_records(session, ctx.group.id, ctx.ids)
    today = date.today()
    try:
        low, high = stats.period_range(period, today, month=month, start=start, end=end,
                                       first=min((r.date for r in records), default=None))
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    in_period = stats.in_range(records, low, high)
    sexes = {uid: u.sex for uid, u in ctx.users.items()}
    changes = goal_changes(session, ctx.ids)
    current, baseline = stats.progress_windows(low, high)
    this_week = stats.monday(today)
    return RankingsOut(
        period=PeriodOut(kind=period, start=low, end=high),
        strength=[StrengthExercise(exercise_id=e.id, exercise=e.name,
                                   dots=strength_rows(ctx, stats.strength_table(in_period, sexes, e.id, "dots")),
                                   absolute=strength_rows(ctx, stats.strength_table(in_period, sexes, e.id, "absolute")))
                  for e in challenge_exercises(session, ctx.group)],
        progress=[ProgressRow(user_id=e.user_id, display_name=ctx.name(e.user_id), pct=r1(e.pct), exercises=e.exercises)
                  for e in (stats.progress_table(records, ctx.ids, current, baseline) if period == "month"
                            else stats.progress_span(records, ctx.ids, low, high))],
        weekly=[WeeklyRow(user_id=e.user_id, display_name=ctx.name(e.user_id), sessions=e.sessions, goal=e.goal,
                          status=e.status)
                for e in stats.weekly_table(records, {uid: stats.goal_in_force(c, this_week) for uid, c in changes.items()},
                                            today)],
        consistency=[ConsistencyRow(user_id=e.user_id, display_name=ctx.name(e.user_id), pct=r1(e.pct), streak=e.streak,
                                    weeks=e.weeks)
                     for e in stats.consistency_table(records, changes, low, high, today)],
    )


def feed_sets(session: Session, ctx: GroupContext) -> tuple[list[stats.SetRecord], dict[int, str]]:
    records = set_records(session, ctx.ids)
    prs = stats.detect_prs(records)
    chosen = sorted((r for r in records if r.set_id in prs), key=stats.chronological_key, reverse=True)
    return chosen, prs


@router.get("/groups/{code}/feed", response_model=list[FeedItem])
def feed(code: str, user: UserDep, session: SessionDep, limit: int = Query(30, ge=1, le=100)) -> list[FeedItem]:
    ctx = context(session, code, user)
    chosen, prs = feed_sets(session, ctx)
    chosen = chosen[:limit]
    ids = [r.set_id for r in chosen]
    counts: dict[int, dict[str, int]] = {i: {"fuerza": 0, "fuego": 0, "dudoso": 0} for i in ids}
    mine: dict[int, str] = {}
    for reaction in session.exec(select(Reaction).where(Reaction.group_id == ctx.group.id, Reaction.set_id.in_(ids))):
        counts[reaction.set_id][reaction.kind] += 1
        if reaction.user_id == user.id:
            mine[reaction.set_id] = reaction.kind
    excluded = excluded_sets(session, ctx.group.id, len(ctx.ids))
    names = {e.id: e.name for e in session.exec(select(Exercise))}
    return [FeedItem(set_id=r.set_id, user_id=r.user_id, display_name=ctx.name(r.user_id), exercise=names[r.exercise_id],
                     date=r.date, weight_kg=r.weight_kg, reps=r.reps, load=r1(r.load), estimated_1rm=r1(r.estimated_1rm),
                     pr=prs[r.set_id], reactions=counts[r.set_id], mine=mine.get(r.set_id),
                     excluded=r.set_id in excluded) for r in chosen]


def require_feed_set(session: Session, ctx: GroupContext, set_id: int) -> None:
    _chosen, prs = feed_sets(session, ctx)
    if set_id not in prs:
        raise HTTPException(status_code=404, detail="Ese PR no está en el feed del grupo")


@router.put("/groups/{code}/feed/{set_id}/reaction", status_code=200)
def react(code: str, set_id: int, data: ReactionInput, user: UserDep, session: SessionDep) -> dict:
    ctx = context(session, code, user)
    require_feed_set(session, ctx, set_id)
    reaction = session.exec(select(Reaction).where(Reaction.group_id == ctx.group.id, Reaction.set_id == set_id,
                                                   Reaction.user_id == user.id)).first()
    if reaction:
        reaction.kind = data.kind
    else:
        session.add(Reaction(group_id=ctx.group.id, set_id=set_id, user_id=user.id, kind=data.kind))
    session.commit()
    return {"kind": data.kind}


@router.delete("/groups/{code}/feed/{set_id}/reaction", status_code=204)
def unreact(code: str, set_id: int, user: UserDep, session: SessionDep) -> Response:
    ctx = context(session, code, user)
    reaction = session.exec(select(Reaction).where(Reaction.group_id == ctx.group.id, Reaction.set_id == set_id,
                                                   Reaction.user_id == user.id)).first()
    if reaction:
        session.delete(reaction)
        session.commit()
    return Response(status_code=204)

import json
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.groups import members_with_users, require_admin
from backend.models import Campaign, Exercise, Routine
from backend.queries import goal_changes, group_records
from backend.routes.rankings import GroupContext, context
from backend.schemas import CampaignInput, CampaignOut, Person, StandingRow

router = APIRouter(prefix="/api")

FIXED_TABLES = {"progress": "Progreso", "consistency": "Constancia"}
MODE_LABELS = {"dots": "DOTS", "absolute": "Absoluto"}


def table_label(session: Session, key: str) -> str:
    if key in FIXED_TABLES:
        return FIXED_TABLES[key]
    mode, _, exercise_id = key.partition(":")
    exercise = session.get(Exercise, int(exercise_id))
    return f"{MODE_LABELS[mode]} {exercise.name}"


def validate_tables(session: Session, tables: list[str]) -> None:
    for key in tables:
        if key in FIXED_TABLES:
            continue
        mode, _, exercise_id = key.partition(":")
        if mode not in MODE_LABELS or not exercise_id.isdigit() or session.get(Exercise, int(exercise_id)) is None:
            raise HTTPException(status_code=422, detail=f"Tabla desconocida: {key}")


def participants(session: Session, ctx: GroupContext, campaign: Campaign) -> list[int]:
    if campaign.routine_id is None:
        return ctx.ids
    return [m.user_id for m, _u in members_with_users(session, ctx.group) if m.routine_id == campaign.routine_id]


def table_order(key: str, records: list[stats.SetRecord], ids: list[int], sexes: dict[int, str],
                changes: dict[int, list], campaign: Campaign, today: date) -> list[int]:
    """Usuarios con datos en esa tabla, del primero al último."""
    window = stats.in_range(records, campaign.start, campaign.end)
    if key == "progress":
        current, baseline = stats.progress_windows(campaign.start, campaign.end)
        return [e.user_id for e in stats.progress_table(records, ids, current, baseline) if e.pct is not None]
    if key == "consistency":
        return [e.user_id for e in stats.consistency_table(records, {u: changes[u] for u in ids}, campaign.start,
                                                           campaign.end, today) if e.pct is not None]
    mode, _, exercise_id = key.partition(":")
    table = stats.strength_table(window, {u: sexes[u] for u in ids}, int(exercise_id), mode)
    return [e.user_id for e in table if e.value is not None]


def campaign_out(session: Session, ctx: GroupContext, campaign: Campaign) -> CampaignOut:
    today = date.today()
    ids = participants(session, ctx, campaign)
    records = group_records(session, ctx.group.id, ids)
    changes = goal_changes(session, ids)
    sexes = {uid: ctx.users[uid].sex for uid in ids}
    tables = json.loads(campaign.tables)
    orders = [table_order(k, records, ids, sexes, changes, campaign, today) for k in tables]
    standings = stats.campaign_points(orders, ids)
    status = "upcoming" if today < campaign.start else "active" if today <= campaign.end else "finished"
    if status == "finished" and campaign.winner_id is None and standings and standings[0].points > 0:
        # El ganador se congela la primera vez que alguien mira la campaña cerrada: es un premio, no un cálculo.
        campaign.winner_id = standings[0].user_id
        campaign.frozen_at = datetime.now(timezone.utc)
        session.commit()
    winner = None
    if campaign.winner_id is not None:
        name = ctx.users[campaign.winner_id].display_name if campaign.winner_id in ctx.users else "ex miembro"
        winner = Person(user_id=campaign.winner_id, display_name=name)
    return CampaignOut(id=campaign.id, name=campaign.name, start=campaign.start, end=campaign.end, tables=tables,
                       table_labels=[table_label(session, k) for k in tables], routine_id=campaign.routine_id,
                       status=status, winner=winner,
                       standings=[StandingRow(user_id=e.user_id, display_name=ctx.name(e.user_id), points=e.points,
                                              firsts=e.firsts) for e in standings])


@router.get("/groups/{code}/campaigns", response_model=list[CampaignOut])
def list_campaigns(code: str, user: UserDep, session: SessionDep) -> list[CampaignOut]:
    ctx = context(session, code, user)
    campaigns = session.exec(select(Campaign).where(Campaign.group_id == ctx.group.id).order_by(Campaign.start.desc()))
    return [campaign_out(session, ctx, c) for c in campaigns]


@router.post("/groups/{code}/campaigns", response_model=CampaignOut, status_code=201)
def create_campaign(code: str, data: CampaignInput, user: UserDep, session: SessionDep) -> CampaignOut:
    group, _ = require_admin(session, code, user)
    if data.start > data.end:
        raise HTTPException(status_code=422, detail="La campaña termina antes de empezar")
    validate_tables(session, data.tables)
    if data.routine_id is not None:
        routine = session.get(Routine, data.routine_id)
        if routine is None or routine.group_id != group.id:
            raise HTTPException(status_code=422, detail="Esa rutina no es de este grupo")
    campaign = Campaign(group_id=group.id, name=data.name, start=data.start, end=data.end,
                        tables=json.dumps(list(dict.fromkeys(data.tables))), routine_id=data.routine_id)
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign_out(session, context(session, code, user), campaign)

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.models import Exercise, RoutineDay, WorkoutSession
from backend.queries import goal_changes, group_records
from backend.routes.me_stats import achievements_of, achievements_out
from backend.routes.rankings import context, r1
from backend.schemas import BroOut, BroSessionOut, FaceOffOut

router = APIRouter(prefix="/api")

LAST_SESSIONS = 5


def recent_sessions(session: Session, records: list[stats.SetRecord], names: dict[int, str]) -> list[BroSessionOut]:
    prs = stats.detect_prs(records)
    by_session: dict[int, list[stats.SetRecord]] = {}
    for r in sorted(records, key=stats.chronological_key, reverse=True):
        by_session.setdefault(r.session_id, []).append(r)
    last = list(by_session.items())[:LAST_SESSIONS]
    query = select(WorkoutSession).where(WorkoutSession.id.in_([sid for sid, _ in last]))
    workouts = {w.id: w for w in session.exec(query)}
    day_ids = {w.routine_day_id for w in workouts.values() if w.routine_day_id}
    days = {d.id: d.name for d in session.exec(select(RoutineDay).where(RoutineDay.id.in_(day_ids)))}
    return [BroSessionOut(date=sets[0].date, routine_day_name=days.get(workouts[sid].routine_day_id), sets=len(sets),
                          prs=sum(1 for r in sets if r.set_id in prs),
                          exercises=list(dict.fromkeys(names[r.exercise_id] for r in reversed(sets))))
            for sid, sets in last]


@router.get("/groups/{code}/members/{user_id}", response_model=BroOut)
def member_profile(code: str, user_id: int, user: UserDep, session: SessionDep) -> BroOut:
    ctx = context(session, code, user)
    if user_id not in ctx.users:
        raise HTTPException(status_code=404, detail="Esa persona no es miembro del grupo")
    bro = ctx.users[user_id]
    today = date.today()
    records = stats.by_user(group_records(session, ctx.group.id, ctx.ids))
    theirs, mine = records.get(user_id, []), records.get(user.id, [])
    changes = goal_changes(session, [user_id])
    this_week = stats.monday(today)
    week = stats.in_range(theirs, this_week, this_week + timedelta(days=6))
    streak = stats.consistency_table(theirs, changes, today, today, today)[0].streak
    names = {e.id: e.name for e in session.exec(select(Exercise))}
    low, high = stats.period_range("6m", today)
    faceoff = [] if user_id == user.id else stats.head_to_head(
        stats.in_range(mine, low, high), stats.in_range(theirs, low, high), user.sex, bro.sex)
    return BroOut(
        user_id=user_id, display_name=bro.display_name, is_me=user_id == user.id,
        weekly_goal=stats.goal_in_force(changes[user_id], this_week), week_days=len(stats.training_days(week)),
        streak=streak,
        achievements=achievements_out(achievements_of(session, [user_id], today)[user_id]),
        faceoff=[FaceOffOut(exercise_id=f.exercise_id, exercise=names[f.exercise_id], mine_1rm=r1(f.mine_1rm),
                            theirs_1rm=r1(f.theirs_1rm), mine_dots=r1(f.mine_dots), theirs_dots=r1(f.theirs_dots),
                            winner=f.winner) for f in faceoff],
        sessions=recent_sessions(session, theirs, names),
    )

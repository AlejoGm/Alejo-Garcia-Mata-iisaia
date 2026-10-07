from datetime import date

from fastapi import APIRouter

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.groups import challenge_exercises
from backend.queries import goal_changes, group_records
from backend.routes.rankings import context, r1
from backend.schemas import DashboardOut, DayActivityOut, LeaderOut, StreakOut, WeekActivityOut

router = APIRouter(prefix="/api")


def prs_between(records: list[stats.SetRecord], start: date, end: date) -> int:
    prs = stats.detect_prs(records)
    return sum(1 for r in records if r.set_id in prs and start <= r.date <= end)


@router.get("/groups/{code}/dashboard", response_model=DashboardOut)
def dashboard(code: str, user: UserDep, session: SessionDep) -> DashboardOut:
    ctx = context(session, code, user)
    records = group_records(session, ctx.group.id, ctx.ids)
    today = date.today()
    series = stats.weekly_activity(records, today, weeks=8)
    this_week = stats.monday(today)
    changes = goal_changes(session, ctx.ids)
    month_start = stats.month_start(today)
    prev_start = stats.shift_months(month_start, -1)

    streaks = [e for e in stats.consistency_table(records, changes, prev_start, today, today) if e.streak > 0]
    best = max(streaks, key=lambda e: e.streak, default=None)

    mine = {r.date for r in records if r.user_id == user.id}
    month = stats.in_range(records, month_start, stats.month_end(today))
    sexes = {uid: u.sex for uid, u in ctx.users.items()}
    leaders = []
    for exercise in challenge_exercises(session, ctx.group):
        top = stats.strength_table(month, sexes, exercise.id, "dots")
        if top and top[0].value is not None:
            leaders.append(LeaderOut(exercise=exercise.name, user_id=top[0].user_id,
                                     display_name=ctx.name(top[0].user_id), value=r1(top[0].value)))

    return DashboardOut(
        sessions=series[-1].sessions, sessions_prev=series[-2].sessions,
        volume=round(series[-1].volume), volume_prev=round(series[-2].volume),
        prs_month=prs_between(records, month_start, stats.month_end(today)),
        prs_prev_month=prs_between(records, prev_start, stats.month_end(prev_start)),
        best_streak=StreakOut(user_id=best.user_id, display_name=ctx.name(best.user_id), weeks=best.streak) if best else None,
        series=[WeekActivityOut(week=w.week, sessions=w.sessions, volume=round(w.volume)) for w in series],
        days=[DayActivityOut(day=d.day, members=d.members, mine=d.day in mine) for d in stats.day_activity(records, today)],
        goal_pct=r1(stats.goal_progress(records, {uid: stats.goal_in_force(c, this_week) for uid, c in changes.items()},
                                        today)),
        leaders=leaders,
    )

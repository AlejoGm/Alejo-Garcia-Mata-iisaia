from datetime import date, timedelta

from fastapi import APIRouter
from sqlmodel import Session, select

from backend import config
from backend.auth import SessionDep, SubDep, UserDep
from backend.models import GoalChange, User, WorkoutSession
from backend.schemas import ConfigOut, ProfileInput, ProfileOut
from backend.stats import goal_in_force as goal_for_week, monday

router = APIRouter(prefix="/api")


@router.get("/config", response_model=ConfigOut)
def get_config() -> ConfigOut:
    return ConfigOut(
        auth=config.AUTH_MODE,
        domain=config.AUTH0_DOMAIN,
        client_id=config.AUTH0_CLIENT_ID,
        audience=config.AUTH0_AUDIENCE,
    )


def last_bodyweight(session: Session, user: User) -> float | None:
    query = (select(WorkoutSession.bodyweight_kg).where(WorkoutSession.user_id == user.id)
             .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc()))
    return session.exec(query).first()


def profile_out(session: Session, user: User) -> ProfileOut:
    changes = [(c.week, c.goal) for c in session.exec(select(GoalChange).where(GoalChange.user_id == user.id))]
    this_week = monday(date.today())
    return ProfileOut(
        id=user.id,
        display_name=user.display_name,
        sex=user.sex,
        unit=user.unit,
        weekly_goal=goal_for_week(changes, this_week),
        next_week_goal=goal_for_week(changes, this_week + timedelta(days=7)),
        last_bodyweight_kg=last_bodyweight(session, user),
    )


def set_goal(session: Session, user: User, goal: int, first_time: bool) -> None:
    this_week = monday(date.today())
    # El primer objetivo rige ya; un cambio rige desde el lunes siguiente.
    week = this_week if first_time else this_week + timedelta(days=7)
    changes = list(session.exec(select(GoalChange).where(GoalChange.user_id == user.id)))
    same_week = next((c for c in changes if c.week == week), None)
    if same_week:
        same_week.goal = goal
    elif goal_for_week([(c.week, c.goal) for c in changes], week) != goal:
        session.add(GoalChange(user_id=user.id, goal=goal, week=week))


@router.get("/me", response_model=ProfileOut)
def get_me(user: UserDep, session: SessionDep) -> ProfileOut:
    return profile_out(session, user)


@router.put("/me", response_model=ProfileOut)
def put_me(data: ProfileInput, sub: SubDep, session: SessionDep) -> ProfileOut:
    user = session.exec(select(User).where(User.sub == sub)).first()
    first_time = user is None
    if user is None:
        user = User(sub=sub, display_name=data.display_name, sex=data.sex, unit=data.unit)
        session.add(user)
        session.flush()
    else:
        user.display_name, user.sex, user.unit = data.display_name, data.sex, data.unit
    set_goal(session, user, data.weekly_goal, first_time)
    session.commit()
    session.refresh(user)
    return profile_out(session, user)

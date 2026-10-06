from fastapi import APIRouter, HTTPException
from sqlmodel import select

from backend.auth import SessionDep, UserDep
from backend.catalog import find_by_name
from backend.models import Exercise
from backend.schemas import ExerciseInput, ExerciseOut

router = APIRouter(prefix="/api")


@router.get("/exercises", response_model=list[ExerciseOut])
def list_exercises(_user: UserDep, session: SessionDep) -> list[Exercise]:
    return list(session.exec(select(Exercise).order_by(Exercise.name)))


@router.post("/exercises", response_model=ExerciseOut, status_code=201)
def create_exercise(data: ExerciseInput, _user: UserDep, session: SessionDep) -> Exercise:
    if find_by_name(session, data.name):
        raise HTTPException(status_code=409, detail=f"Ya existe el ejercicio '{data.name}'")
    exercise = Exercise(name=data.name, bodyweight=data.bodyweight)
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise

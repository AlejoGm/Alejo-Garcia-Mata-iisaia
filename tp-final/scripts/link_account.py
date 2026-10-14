"""Le pasa una cuenta de Google a un usuario de desarrollo, para no perder su historia al activar Auth0.

    uv run python -m scripts.link_account alejo [--sub google-oauth2|123]

Sin `--sub` usa la última cuenta que no es de desarrollo: la que se crea al entrar con Google y completar el perfil.
Esa cuenta tiene que estar vacía (sin sesiones ni grupos); se borra y su `sub` pasa a `dev|alejo`.
"""
import argparse

from sqlmodel import Session, delete, select

from backend.db import engine
from backend.models import GoalChange, Member, User, WorkoutSession


def link(name: str, sub: str | None) -> None:
    with Session(engine) as session:
        old = session.exec(select(User).where(User.sub == f"dev|{name.lower()}")).first()
        if old is None:
            raise SystemExit(f"No existe el usuario de desarrollo '{name}'.")
        query = select(User).where(User.sub == sub) if sub else (
            select(User).where(User.sub.not_like("dev|%")).order_by(User.created_at.desc()))
        new = session.exec(query).first()
        if new is None:
            raise SystemExit("No hay cuenta de Google: entrá una vez con Google y completá el perfil.")
        used = session.exec(select(WorkoutSession).where(WorkoutSession.user_id == new.id)).first() or \
            session.exec(select(Member).where(Member.user_id == new.id)).first()
        if used:
            raise SystemExit(f"La cuenta {new.sub} ya tiene sesiones o grupos: no la piso.")
        google_sub = new.sub
        session.exec(delete(GoalChange).where(GoalChange.user_id == new.id))
        session.delete(new)
        session.flush()
        old.sub = google_sub
        session.commit()
        print(f"Listo: '{old.display_name}' ahora entra con {google_sub}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pasa una cuenta de Google a un usuario de desarrollo.")
    parser.add_argument("name", help="nombre del usuario de desarrollo (el que se usaba para entrar)")
    parser.add_argument("--sub", help="sub de la cuenta de Google; por defecto, la última creada")
    args = parser.parse_args()
    link(args.name, args.sub)


if __name__ == "__main__":
    main()

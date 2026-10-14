from fastapi import APIRouter, Header, HTTPException, Response
from sqlmodel import select

from backend import config
from backend.auth import SessionDep, local_sub
from backend.models import AuthToken, Credential
from backend.passwords import hash_password, new_token, token_hash, verify_password
from backend.schemas import AccountInput, LoginInput, TokenOut

router = APIRouter(prefix="/api/auth")


def require_local() -> None:
    if config.AUTH_MODE != "local":
        raise HTTPException(status_code=404, detail="Las cuentas con contraseña no están activas en este servidor")


def issue(session: SessionDep, sub: str) -> TokenOut:
    token = new_token()
    session.add(AuthToken(token_hash=token_hash(token), sub=sub))
    session.commit()
    return TokenOut(token=token)


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: AccountInput, session: SessionDep) -> TokenOut:
    require_local()
    if session.get(Credential, data.username):
        raise HTTPException(status_code=409, detail=f"El usuario '{data.username}' ya existe")
    # Las cuentas locales usan el mismo sub que el modo desarrollo: registrarse con un nombre que ya tenía
    # historia (por ejemplo, de los datos de prueba) se queda con ese usuario.
    sub = local_sub(data.username)
    session.add(Credential(username=data.username, sub=sub, password_hash=hash_password(data.password)))
    return issue(session, sub)


@router.post("/login", response_model=TokenOut, status_code=200)
def login(data: LoginInput, session: SessionDep) -> TokenOut:
    require_local()
    credential = session.get(Credential, data.username)
    if credential is None or not verify_password(data.password, credential.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return issue(session, credential.sub)


@router.post("/logout", status_code=204)
def logout(session: SessionDep, authorization: str | None = Header(None)) -> Response:
    if authorization and authorization.lower().startswith("bearer "):
        query = select(AuthToken).where(AuthToken.token_hash == token_hash(authorization[7:].strip()))
        stored = session.exec(query).first()
        if stored:
            session.delete(stored)
            session.commit()
    return Response(status_code=204)

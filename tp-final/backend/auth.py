from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from backend import config
from backend.db import get_session
from backend.models import User

DEV_PREFIX = "dev:"

_jwks_client: jwt.PyJWKClient | None = None


def _jwks() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(f"https://{config.AUTH0_DOMAIN}/.well-known/jwks.json")
    return _jwks_client


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def sub_from_dev_token(token: str) -> str:
    name = token[len(DEV_PREFIX):].strip().lower()
    if not token.startswith(DEV_PREFIX) or not name:
        raise _unauthorized("Token de desarrollo inválido")
    return f"dev|{name}"


def sub_from_auth0_token(token: str) -> str:
    try:
        key = _jwks().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=config.AUTH0_AUDIENCE,
            issuer=f"https://{config.AUTH0_DOMAIN}/",
        )
    except jwt.PyJWTError as err:
        raise _unauthorized("Token inválido o vencido") from err
    return claims["sub"]


def current_sub(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Falta iniciar sesión")
    token = authorization[7:].strip()
    if config.AUTH_MODE == "dev":
        return sub_from_dev_token(token)
    return sub_from_auth0_token(token)


SubDep = Annotated[str, Depends(current_sub)]
SessionDep = Annotated[Session, Depends(get_session)]


def current_user(sub: SubDep, session: SessionDep) -> User:
    user = session.exec(select(User).where(User.sub == sub)).first()
    if user is None:
        # El frontend lo usa para mandar a completar el perfil.
        raise HTTPException(status_code=409, detail="perfil incompleto")
    return user


UserDep = Annotated[User, Depends(current_user)]

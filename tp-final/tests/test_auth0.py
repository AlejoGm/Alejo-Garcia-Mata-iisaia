from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from backend import auth, config

DOMAIN = "gymbro.test.auth0.com"
AUDIENCE = "https://gymbro/api"


@pytest.fixture
def auth0_mode(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(config, "AUTH_MODE", "auth0")
    monkeypatch.setattr(config, "AUTH0_DOMAIN", DOMAIN)
    monkeypatch.setattr(config, "AUTH0_AUDIENCE", AUDIENCE)
    fake = SimpleNamespace(get_signing_key_from_jwt=lambda _t: SimpleNamespace(key=key.public_key()))
    monkeypatch.setattr(auth, "_jwks", lambda: fake)
    return key


def token(key, **overrides):
    claims = {"sub": "google-oauth2|123", "aud": AUDIENCE, "iss": f"https://{DOMAIN}/", **overrides}
    return jwt.encode(claims, key, algorithm="RS256")


def test_valid_auth0_token_gives_the_sub(auth0_mode):
    assert auth.current_sub(f"Bearer {token(auth0_mode)}") == "google-oauth2|123"


def test_wrong_audience_is_401(auth0_mode):
    with pytest.raises(auth.HTTPException) as err:
        auth.current_sub(f"Bearer {token(auth0_mode, aud='otra')}")
    assert err.value.status_code == 401


def test_dev_token_is_rejected_when_auth0_is_configured(auth0_mode):
    with pytest.raises(auth.HTTPException) as err:
        auth.current_sub("Bearer dev:ana")
    assert err.value.status_code == 401

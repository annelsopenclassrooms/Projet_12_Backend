import jwt
import pytest
from datetime import datetime, timedelta, timezone
from app.utils import jwt_handler


class DummyRole:
    def __init__(self, name):
        self.name = name


class DummyUser:
    def __init__(self, user_id=1, username="testuser", role="admin"):
        self.id = user_id
        self.username = username
        self.role = DummyRole(role)


# ======= Tests create_jwt_token ======= #
def test_create_jwt_token_returns_string():
    user = DummyUser()
    token = jwt_handler.create_jwt_token(user)
    assert isinstance(token, str)
    decoded = jwt.decode(token, jwt_handler.SECRET_KEY, algorithms=[jwt_handler.ALGORITHM])
    assert decoded["sub"] == str(user.id)
    assert decoded["username"] == user.username
    assert decoded["role"] == user.role.name


# ======= Tests decode_jwt_token (valid token) ======= #
def test_decode_jwt_token_valid():
    user = DummyUser()
    token = jwt_handler.create_jwt_token(user)
    payload, error = jwt_handler.decode_jwt_token(token)
    assert error is None
    assert payload["username"] == "testuser"
    assert payload["role"] == "admin"


# ======= Tests decode_jwt_token (invalid token) ======= #
def test_decode_jwt_token_invalid():
    invalid_token = "abc.def.ghi"
    payload, error = jwt_handler.decode_jwt_token(invalid_token)
    assert payload is None
    assert error == "Token invalide"


# ======= Tests decode_jwt_token (expired token) ======= #
def test_decode_jwt_token_expired(monkeypatch):
    """
    On force la date d'expiration dans le passé pour tester l'expiration.
    """
    user = DummyUser()

    # Monkeypatch TOKEN_EXPIRE_MINUTES to -1 to force expiration
    monkeypatch.setattr(jwt_handler, "TOKEN_EXPIRE_MINUTES", -1)
    expired_token = jwt_handler.create_jwt_token(user)

    payload, error = jwt_handler.decode_jwt_token(expired_token)
    assert payload is None
    assert error == "Token expiré"

    # Reset
    monkeypatch.setattr(jwt_handler, "TOKEN_EXPIRE_MINUTES", 1000)

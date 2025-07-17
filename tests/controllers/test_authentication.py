import pytest
from sqlalchemy.orm import Session
from app.models import Users
from app.controllers.auth_controller import authenticate_user


class FakeSession:
    def __init__(self, fake_user):
        self.fake_user = fake_user

    def query(self, model):
        return self

    def filter(self, *args):
        class Query:
            def first(inner_self):
                return self.fake_user
        return Query()


def test_authenticate_user_success(monkeypatch):
    fake_user = Users(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed123",
        first_name="Test",
        last_name="User"
    )

    # monkeypatch de verify_password pour retourner True
    monkeypatch.setattr("app.controllers.auth_controller.verify_password", lambda p, h: True)

    session = FakeSession(fake_user)
    user, error = authenticate_user(session, "test@example.com", "plainpassword")

    assert error is None
    assert user == fake_user


def test_authenticate_user_wrong_password(monkeypatch):
    fake_user = Users(
        id=2,
        username="wronguser",
        email="wrong@example.com",
        hashed_password="hashed123",
        first_name="Wrong",
        last_name="User"
    )

    monkeypatch.setattr("app.controllers.auth_controller.verify_password", lambda p, h: False)

    session = FakeSession(fake_user)
    user, error = authenticate_user(session, "wrong@example.com", "wrongpassword")

    assert user is None
    assert error == "Identifiants invalides."


def test_authenticate_user_not_found(monkeypatch):
    session = FakeSession(None)

    # même si verify_password est correct, aucun user trouvé
    monkeypatch.setattr("app.controllers.auth_controller.verify_password", lambda p, h: True)

    user, error = authenticate_user(session, "unknown@example.com", "password")

    assert user is None
    assert error == "Identifiants invalides."

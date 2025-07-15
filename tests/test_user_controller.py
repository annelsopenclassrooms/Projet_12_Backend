import pytest
from app.controllers.user_controller import create_user, update_user
from app.models import Users, Roles


# === Fakes de base ===

class FakeQuery:
    def __init__(self, return_value):
        self.return_value = return_value
        self.second_value = None  # pour cas de doublon

    def filter_by(self, **kwargs):
        return self

    def filter(self, *args):
        return self

    def first(self):
        if self.second_value is not None:
            return self.second_value
        return self.return_value


class FakeSession:
    def __init__(self):
        self.added = None
        self.committed = False
        self.query_data = []

    def query(self, model):
        return FakeQuery(self.query_data.pop(0))

    def add(self, obj):
        obj.id = 123
        self.added = obj

    def commit(self):
        self.committed = True


# === Monkeypatch externes ===

def fake_hash_password(password):
    return f"hashed-{password}"

def fake_capture_message(*args, **kwargs):
    pass


# === TESTS CREATE_USER ===

def test_create_user_success(monkeypatch):
    session = FakeSession()
    session.query_data = [
        Roles(id=1, name="support"),
        None  # aucun utilisateur existant avec cet email
    ]

    monkeypatch.setattr("app.controllers.user_controller.hash_password", fake_hash_password)
    monkeypatch.setattr("app.controllers.user_controller.sentry_sdk.capture_message", fake_capture_message)

    user, error = create_user(
        session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="jdoe@example.com",
        password="secret123",
        role_name="support"
    )

    assert error is None
    assert user.username == "jdoe"
    assert user.hashed_password == "hashed-secret123"
    assert user.role_id == 1
    assert session.committed


def test_create_user_role_not_found(monkeypatch):
    session = FakeSession()
    session.query_data = [None]  # rôle introuvable

    user, error = create_user(
        session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="jdoe@example.com",
        password="secret123",
        role_name="unknown"
    )

    assert user is None
    assert error == "❌ Rôle 'unknown' introuvable."


def test_create_user_email_exists(monkeypatch):
    session = FakeSession()
    session.query_data = [
        Roles(id=1, name="support"),
        Users(id=99, email="jdoe@example.com")  # utilisateur déjà existant
    ]

    user, error = create_user(
        session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="jdoe@example.com",
        password="secret123",
        role_name="support"
    )

    assert user is None
    assert error == "❌ Un utilisateur existe déjà avec cet email : jdoe@example.com"


# === TESTS UPDATE_USER ===

def test_update_user_success(monkeypatch):
    session = FakeSession()
    existing_user = Users(id=1, username="old", first_name="Old", email="old@example.com", role_id=1)
    session.query_data = [existing_user]

    monkeypatch.setattr("app.controllers.user_controller.hash_password", fake_hash_password)
    monkeypatch.setattr("app.controllers.user_controller.sentry_sdk.capture_message", fake_capture_message)

    updates = {
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
        "email": "new@example.com",
        "password": "newpass123",
        "role_name": "gestion"
    }

    session.query_data.append(None)  # Pas de doublon d'email
    session.query_data.append(Roles(id=2, name="gestion"))

    updated, error = update_user(session, user_id=1, **updates)

    assert error is None
    assert updated.username == "newuser"
    assert updated.email == "new@example.com"
    assert updated.hashed_password == "hashed-newpass123"
    assert updated.role_id == 2
    assert session.committed


def test_update_user_not_found():
    session = FakeSession()
    session.query_data = [None]  # user introuvable

    updated, error = update_user(session, user_id=999, username="nobody")

    assert updated is None
    assert error == "❌ Utilisateur avec ID 999 introuvable."


def test_update_user_email_conflict():
    session = FakeSession()
    user = Users(id=1, email="original@example.com")
    session.query_data = [user]
    session.query_data.append(Users(id=2, email="conflict@example.com"))  # doublon

    updated, error = update_user(session, user_id=1, email="conflict@example.com")

    assert updated is None
    assert error == "❌ Un autre utilisateur a déjà cet email : conflict@example.com"


def test_update_user_invalid_role():
    session = FakeSession()
    user = Users(id=1)
    session.query_data = [user]
    session.query_data.append(None)  # rôle inexistant

    updated, error = update_user(session, user_id=1, role_name="invalid")

    assert updated is None
    assert error == "❌ Rôle 'invalid' introuvable."

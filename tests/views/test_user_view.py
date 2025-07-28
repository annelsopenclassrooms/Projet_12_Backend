import sys
from unittest.mock import MagicMock
import pytest
from app.models import Users

# Neutraliser les décorateurs AVANT l'import de user_view
if 'app.views.user_view' in sys.modules:
    del sys.modules['app.views.user_view']

mock_auth = MagicMock()
mock_auth.jwt_required = lambda f: f
mock_auth.role_required = lambda *roles: (lambda f: f)
sys.modules['app.utils.auth'] = mock_auth

import app.views.user_view as user_view


# === Fakes ===
class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeUser:
    def __init__(self, user_id=1, role_name="gestion"):
        self.id = user_id
        self.username = "user" + str(user_id)
        self.first_name = "Jean"
        self.last_name = "Dupont"
        self.email = f"user{user_id}@test.com"
        self.role = FakeRole(role_name)


# === Helpers ===
class AskMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index] if self.index < len(self.responses) else kwargs.get("default", "")
        self.index += 1
        return res


class ConfirmMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index] if self.index < len(self.responses) else kwargs.get("default", False)
        self.index += 1
        return res


class FakeSession:
    def __init__(self, users=None):
        self.users = users or [FakeUser(1), FakeUser(2)]
        self.deleted = []
        self.updated = []
        self.committed = False

    def query(self, model):
        return FakeQuery(self.users)

    def close(self):
        pass


class FakeQuery:
    def __init__(self, items):
        self.items = items
    def all(self):
        return self.items
    def get(self, id):
        return next((u for u in self.items if u.id == id), None)


class FakeSessionFactory:
    def __init__(self, users=None):
        self.session = FakeSession(users)
    def __call__(self):
        return self.session


# === Tests ===
def test_create_user_view_success(monkeypatch):
    fake_user = FakeUser(role_name="gestion")
    monkeypatch.setattr(user_view.Prompt, "ask", AskMock([
        "newuser", "Jean", "Dupont", "new@example.com", "password123", "gestion"
    ]))
    monkeypatch.setattr(user_view, "SessionLocal", FakeSessionFactory())
    monkeypatch.setattr(user_view, "create_user", lambda s, **k: (FakeUser(), None))

    user_view.create_user_view(fake_user)


def test_create_user_view_error(monkeypatch):
    fake_user = FakeUser(role_name="gestion")
    monkeypatch.setattr(user_view.Prompt, "ask", AskMock([
        "baduser", "Jean", "Dupont", "bad@example.com", "123", "gestion"
    ]))
    monkeypatch.setattr(user_view, "SessionLocal", FakeSessionFactory())
    monkeypatch.setattr(user_view, "create_user", lambda s, **k: (None, "Erreur de création"))

    user_view.create_user_view(fake_user)


def test_update_user_view_success(monkeypatch):
    fake_user = FakeUser(role_name="gestion")
    monkeypatch.setattr(user_view.Prompt, "ask", AskMock([
        "1", "newuser", "Jean", "Dupont", "updated@example.com", "gestion"
    ]))
    monkeypatch.setattr(user_view.Confirm, "ask", ConfirmMock([False]))
    monkeypatch.setattr(user_view, "SessionLocal", FakeSessionFactory())
    monkeypatch.setattr(user_view, "update_user", lambda s, uid, **k: (FakeUser(), None))

    user_view.update_user_view(fake_user)


def test_update_user_view_invalid_id(monkeypatch):
    fake_user = FakeUser(role_name="gestion")
    monkeypatch.setattr(user_view.Prompt, "ask", AskMock([
        "abc"  # ID invalide
    ]))
    monkeypatch.setattr(user_view, "SessionLocal", FakeSessionFactory())

    user_view.update_user_view(fake_user)


def test_show_all_users_view(monkeypatch):
    fake_user = FakeUser(role_name="gestion")
    monkeypatch.setattr(user_view, "SessionLocal", FakeSessionFactory())
    user_view.show_all_users_view(fake_user)

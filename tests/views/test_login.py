import pytest
import builtins
import app.views.login as login_view
from pathlib import Path


def test_login_success(monkeypatch, tmp_path):
    fake_user = FakeUser("Anne", "gestion")
    token_file = tmp_path / ".token"

    monkeypatch.setattr(builtins, "input", InputMock(["anne@example.com"]))
    monkeypatch.setattr(login_view, "getpass", GetPassMock(["supersecret"]))  # <- IMPORTANT
    monkeypatch.setattr(login_view, "authenticate_user", AuthMock(user=fake_user))
    monkeypatch.setattr(login_view, "create_jwt_token", TokenMock("FAKE.TOKEN.123"))
    monkeypatch.setattr(login_view, "TOKEN_FILE", str(token_file))
    monkeypatch.setattr(login_view, "SessionLocal", FakeSessionFactory())

    user = login_view.login()

    assert user == fake_user
    assert token_file.exists()
    assert token_file.read_text() == "FAKE.TOKEN.123"


def test_login_auth_failure(monkeypatch):
    monkeypatch.setattr(builtins, "input", InputMock(["fail@example.com"]))
    monkeypatch.setattr(login_view, "getpass", GetPassMock(["wrongpass"]))  # <- IMPORTANT
    monkeypatch.setattr(login_view, "authenticate_user", AuthMock(user=None, error="Invalid credentials"))
    monkeypatch.setattr(login_view, "SessionLocal", FakeSessionFactory())

    user = login_view.login()

    assert user is None


# === MOCKS ===

class FakeRole:
    def __init__(self, name):
        self.name = name

class FakeUser:
    def __init__(self, first_name, role_name):
        self.first_name = first_name
        self.role = FakeRole(role_name)
    def __eq__(self, other):
        return isinstance(other, FakeUser) and self.first_name == other.first_name and self.role.name == other.role.name

class InputMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        result = self.responses[self.index]
        self.index += 1
        return result

class GetPassMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        result = self.responses[self.index]
        self.index += 1
        return result

class AuthMock:
    def __init__(self, user=None, error=None):
        self.user = user
        self.error = error
    def __call__(self, session, login_input, password):
        return self.user, self.error

class TokenMock:
    def __init__(self, token):
        self.token = token
    def __call__(self, user):
        return self.token

class FakeSession:
    def close(self): pass

class FakeSessionFactory:
    def __call__(self):
        return FakeSession()

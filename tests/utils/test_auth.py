import os
import builtins
import pytest

from app.utils import auth


# ======= Fixtures ======= #
@pytest.fixture(autouse=True)
def cleanup_token_file():
    # Supprime le fichier token avant et après chaque test
    if os.path.exists(auth.TOKEN_FILE):
        os.remove(auth.TOKEN_FILE)
    yield
    if os.path.exists(auth.TOKEN_FILE):
        os.remove(auth.TOKEN_FILE)


class DummyUser:
    def __init__(self, role_name="gestion"):
        self.id = 1
        self.role = type("Role", (), {"name": role_name})


# ======= Tests get_current_user ======= #
def test_get_current_user_no_token(monkeypatch, capsys):
    # Pas de fichier .token
    user = auth.get_current_user()
    captured = capsys.readouterr()
    assert "🔒 Vous n'êtes pas connecté." in captured.out
    assert user is None


def test_get_current_user_invalid_token(monkeypatch, capsys):
    # Crée un token fictif
    with open(auth.TOKEN_FILE, "w") as f:
        f.write("FAKE_TOKEN")

    # Simule decode_jwt_token qui retourne une erreur
    def fake_decode(token):
        return None, "Token invalide"
    monkeypatch.setattr(auth, "decode_jwt_token", fake_decode)

    user = auth.get_current_user()
    captured = capsys.readouterr()
    assert "❌ Erreur d'authentification" in captured.out
    assert user is None


def test_get_current_user_valid(monkeypatch):
    # Crée un token valide
    with open(auth.TOKEN_FILE, "w") as f:
        f.write("VALID_TOKEN")

    payload = {"sub": 123}

    def fake_decode(token):
        return payload, None

    dummy_user = DummyUser()

    class DummySession:
        def query(self, model):
            return self
        def get(self, user_id):
            return dummy_user

    monkeypatch.setattr(auth, "decode_jwt_token", fake_decode)
    monkeypatch.setattr(auth, "SessionLocal", lambda: DummySession())

    user = auth.get_current_user()
    assert isinstance(user, DummyUser)


# ======= Tests jwt_required ======= #
def test_jwt_required_not_logged(monkeypatch, capsys):
    def func(user):
        return "ok"

    decorated = auth.jwt_required(func)

    # Simule get_current_user qui retourne None
    monkeypatch.setattr(auth, "get_current_user", lambda: None)

    result = decorated()
    captured = capsys.readouterr()
    assert "⛔ Accès refusé" in captured.out
    assert result is None


def test_jwt_required_logged(monkeypatch):
    def func(user):
        return f"Hello {user.role.name}"

    decorated = auth.jwt_required(func)

    monkeypatch.setattr(auth, "get_current_user", lambda: DummyUser())

    result = decorated()
    assert result == "Hello gestion"


# ======= Tests role_required ======= #
def test_role_required_authorized():
    @auth.role_required("gestion", "admin")
    def restricted_function(user):
        return "Access Granted"

    user = DummyUser(role_name="gestion")
    assert restricted_function(user) == "Access Granted"


def test_role_required_unauthorized(capsys):
    @auth.role_required("admin")
    def restricted_function(user):
        return "Access Granted"

    user = DummyUser(role_name="support")
    result = restricted_function(user)
    captured = capsys.readouterr()
    assert "⛔ Accès refusé" in captured.out
    assert result is None

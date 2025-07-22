import pytest
from app.views import user_view

# ==== Classes Factices ==== #
class DummyRole:
    def __init__(self, name="gestion"):
        self.name = name

class DummyUser:
    def __init__(
        self,
        user_id=1,
        username="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        role_name="gestion",
    ):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = DummyRole(role_name)


# Session simulée
class DummySession:
    def __init__(self, users=None):
        self._users = users or [DummyUser()]
        self.deleted = []
        self.committed = False

    def query(self, model):
        return self

    def all(self):
        return self._users

    def get(self, user_id):
        return next((u for u in self._users if u.id == user_id), None)

    def delete(self, user):
        self.deleted.append(user)

    def commit(self):
        self.committed = True

    def close(self):
        pass


# ==== Fixtures ==== #
@pytest.fixture
def mock_session(monkeypatch):
    dummy_session = DummySession()

    def session_factory():
        return dummy_session

    monkeypatch.setattr(user_view, "SessionLocal", session_factory)
    return dummy_session


@pytest.fixture
def mock_prompts(monkeypatch):
    answers = {}

    def set_answer(prompt, value):
        answers[prompt] = value

    def fake_ask(prompt, **kwargs):
        return answers.get(prompt, kwargs.get("default", ""))

    def fake_confirm(prompt, default=False):
        return answers.get(prompt, default)

    monkeypatch.setattr(user_view.Prompt, "ask", fake_ask)
    monkeypatch.setattr(user_view.Confirm, "ask", fake_confirm)
    return set_answer


# ==== TESTS CREATE ==== #
def test_create_user_view_success(mock_session, mock_prompts, monkeypatch):
    mock_prompts("Nom d'utilisateur", "newuser")
    mock_prompts("Prénom", "New")
    mock_prompts("Nom", "User")
    mock_prompts("Email", "new@example.com")
    mock_prompts("Mot de passe", "password123")
    mock_prompts("Rôle", "gestion")

    def mock_create_user(session, data):
        return True, DummyUser(username="newuser")

    monkeypatch.setattr("app.controllers.user_controller.create_user", mock_create_user)

    user_view.create_user_view(DummyUser())


def test_create_user_view_error(mock_session, mock_prompts, monkeypatch):
    mock_prompts("Nom d'utilisateur", "baduser")
    mock_prompts("Prénom", "Bad")
    mock_prompts("Nom", "User")
    mock_prompts("Email", "bad@example.com")
    mock_prompts("Mot de passe", "123")
    mock_prompts("Rôle", "gestion")

    def mock_create_user(session, data):
        return False, "Erreur de création"

    monkeypatch.setattr("app.controllers.user_controller.create_user", mock_create_user)

    user_view.create_user_view(DummyUser())


# ==== TESTS UPDATE ==== #
def test_update_user_view_success(mock_session, mock_prompts, monkeypatch):
    mock_prompts("ID de l'utilisateur à modifier", "1")
    mock_prompts("Nouveau prénom", "Updated")
    mock_prompts("Nouveau nom", "User")
    mock_prompts("Nouvel email", "updated@example.com")
    mock_prompts("Nouveau mot de passe", "newpassword")
    mock_prompts("Nouveau rôle", "gestion")

    def mock_update_user(session, user_id, data):
        return True, DummyUser(username="updateduser")

    monkeypatch.setattr("app.controllers.user_controller.update_user", mock_update_user)

    user_view.update_user_view(DummyUser())


def test_update_user_view_invalid_id(mock_session, mock_prompts):
    mock_prompts("ID de l'utilisateur à modifier", "abc")
    user_view.update_user_view(DummyUser())


# ==== TESTS DELETE ==== #
def test_delete_user_view_confirm(mock_session, mock_prompts, monkeypatch):
    mock_prompts("ID de l'utilisateur à supprimer", "1")
    mock_prompts("Confirmer la suppression de testuser ?", True)

    def mock_delete_user_view(current_user):
        return True, None

    monkeypatch.setattr(user_view, "delete_user_view", mock_delete_user_view)

    user_view.delete_user_view(DummyUser())


def test_delete_user_view_cancel(mock_session, mock_prompts, monkeypatch):
    mock_prompts("ID de l'utilisateur à supprimer", "1")
    mock_prompts("Confirmer la suppression de testuser ?", False)

    def mock_delete_user_view(current_user):
        return True, None

    monkeypatch.setattr(user_view, "delete_user_view", mock_delete_user_view)

    user_view.delete_user_view(DummyUser())


def test_delete_user_view_invalid_id(mock_session, mock_prompts):
    mock_prompts("ID de l'utilisateur à supprimer", "abc")
    user_view.delete_user_view(DummyUser())


# ==== TESTS SHOW ==== #
def test_show_all_users_view(mock_session):
    # Pas de current_user=... car décorateur injecte déjà l'utilisateur
    user_view.show_all_users_view()

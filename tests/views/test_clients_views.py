import pytest
from unittest.mock import MagicMock
from app.views.client_view import show_all_clients_view, create_client_view, update_client_view

# ---------------------
# FAKES
# ---------------------

class FakeUser:
    id = 1
    first_name = "Alice"
    role = "commercial"

class FakeClient:
    id = 1
    first_name = "Jean"
    last_name = "Dupont"
    email = "jean@client.com"
    phone = "0600000000"
    company_name = "TestCorp"
    commercial_id = 1

# ---------------------
# FIXTURES
# ---------------------

@pytest.fixture
def fake_user():
    return FakeUser()

@pytest.fixture
def fake_session(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr("app.views.client_view.SessionLocal", lambda: session)
    return session


# ---------------------
# TEST show_all_clients_view
# ---------------------

def test_show_all_clients_view(monkeypatch, fake_session, fake_user):
    def mock_list_all_clients(session):
        return [FakeClient()]
    
    monkeypatch.setattr("app.views.client_view.list_all_clients", mock_list_all_clients)

    show_all_clients_view(fake_user)


# ---------------------
# TEST create_client_view
# ---------------------

def test_create_client_view(monkeypatch, fake_session, fake_user):
    inputs = {
        "Prénom": "Emma",
        "Nom": "Durand",
        "Téléphone": "0123456789",
        "Nom de l'entreprise": "Durand SARL"
    }

    def mock_prompt_ask(message, **kwargs):
        return inputs[message]

    def mock_safe_input_email(msg):
        return "emma@durand.com"

    def mock_create_client(session, **kwargs):
        client = FakeClient()
        client.first_name = kwargs["first_name"]
        client.last_name = kwargs["last_name"]
        return client, None

    monkeypatch.setattr("app.views.client_view.Prompt.ask", mock_prompt_ask)
    monkeypatch.setattr("app.views.client_view.safe_input_email", mock_safe_input_email)
    monkeypatch.setattr("app.views.client_view.create_client", mock_create_client)

    create_client_view(fake_user)


# ---------------------
# TEST update_client_view
# ---------------------

def test_update_client_view(monkeypatch, fake_session, fake_user):
    client = FakeClient()

    fake_session.query().filter_by().all.return_value = [client]
    fake_session.query().filter_by().first.return_value = client

    def mock_safe_input_int(msg):
        return 1

    def mock_prompt_ask(msg, **kwargs):
        if msg.startswith("Nouveau prénom"):
            return "NouveauPrenom"
        if msg.startswith("Nouveau nom"):
            return "NouveauNom"
        if msg.startswith("Nouvelle société"):
            return "NouvelleSociété"
        if msg.startswith("Nouvel email"):
            return "nouveau@mail.com"
        if msg.startswith("Nouveau téléphone"):
            return "0700000000"
        return kwargs.get("default", "")

    def mock_safe_input_email(msg, default=None):
        return "nouveau@mail.com"

    def mock_safe_input_phone(msg, default=None):
        return "0700000000"

    def mock_confirm_ask(msg, default=False):
        return True

    def mock_update_client(session, client_id, updates, current_user):
        client.first_name = updates["first_name"]
        client.last_name = updates["last_name"]
        return client, None

    monkeypatch.setattr("app.views.client_view.safe_input_int", mock_safe_input_int)
    monkeypatch.setattr("app.views.client_view.Prompt.ask", mock_prompt_ask)
    monkeypatch.setattr("app.views.client_view.safe_input_email", mock_safe_input_email)
    monkeypatch.setattr("app.views.client_view.safe_input_phone", mock_safe_input_phone)
    monkeypatch.setattr("app.views.client_view.Confirm.ask", mock_confirm_ask)
    monkeypatch.setattr("app.views.client_view.update_client", mock_update_client)

    update_client_view(fake_user)

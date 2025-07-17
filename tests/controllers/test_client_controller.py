import pytest
from app.models import Clients
from app.controllers.client_controller import create_client, update_client


class DummyUser:
    def __init__(self, id, role_name):
        self.id = id
        self.role = type("Role", (), {"name": role_name})()


@pytest.fixture
def fake_session():
    class Session:
        query = None  # Pour autoriser le monkeypatch

        def __init__(self):
            self._added = None
            self._committed = False
            self._rolled_back = False

        def add(self, obj):
            self._added = obj

        def commit(self):
            self._committed = True

        def rollback(self):
            self._rolled_back = True

    return Session()


# === MOCKS POUR CREATE CLIENT ===

class FakeQueryNone:
    def filter_by(self, **kwargs):
        return self
    def first(self):
        return None

class FakeQueryExistingClient:
    def filter_by(self, **kwargs):
        return self
    def first(self):
        return Clients(email="test@example.com")


# === TESTS CREATE CLIENT ===

def test_create_client_success(monkeypatch, fake_session):
    def mock_query(model):
        return FakeQueryNone()
    monkeypatch.setattr(fake_session, "query", mock_query)

    client, error = create_client(
        fake_session, "Alice", "Martin", "alice@example.com", "0123456789", "CompanyX", 1
    )

    assert error is None
    assert client.first_name == "Alice"
    assert fake_session._added == client
    assert fake_session._committed is True


def test_create_client_existing_email(monkeypatch, fake_session):
    def mock_query(model):
        return FakeQueryExistingClient()
    monkeypatch.setattr(fake_session, "query", mock_query)

    client, error = create_client(
        fake_session, "Alice", "Martin", "test@example.com", "0123456789", "CompanyX", 1
    )

    assert client is None
    assert "existe déjà" in error
    assert fake_session._committed is False


def test_create_client_exception(monkeypatch, fake_session):
    def mock_query(model):
        return FakeQueryNone()

    def failing_commit():
        raise Exception("Erreur BDD")

    monkeypatch.setattr(fake_session, "query", mock_query)
    monkeypatch.setattr(fake_session, "commit", failing_commit)

    client, error = create_client(
        fake_session, "Bob", "Durand", "bob@example.com", "0987654321", "CompanyY", 2
    )

    assert client is None
    assert "Erreur inattendue" in error
    assert fake_session._rolled_back is True


# === MOCKS POUR UPDATE CLIENT ===

class FakeQueryUpdate:
    def __init__(self, client, existing_email=None):
        self.client = client
        self.existing_email = existing_email
        self.call_count = 0

    def filter_by(self, **kwargs):
        return self

    def first(self):
        self.call_count += 1
        if self.call_count == 1:
            return self.client
        elif self.existing_email:
            return self.existing_email
        return None


# === TESTS UPDATE CLIENT ===

def test_update_client_success(monkeypatch, fake_session):
    client = Clients(id=1, first_name="Old", last_name="Name", email="old@example.com", commercial_id=42)

    def mock_query(model):
        return FakeQueryUpdate(client)  # simulate no email conflict

    monkeypatch.setattr(fake_session, "query", mock_query)

    current_user = DummyUser(42, "commercial")
    updates = {"first_name": "New", "email": "new@example.com"}

    updated_client, error = update_client(fake_session, 1, updates, current_user)

    assert error is None
    assert updated_client.first_name == "New"
    assert updated_client.email == "new@example.com"
    assert fake_session._committed is True


def test_update_client_not_found(monkeypatch, fake_session):
    class FakeQueryNotFound:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return None

    def mock_query(model):
        return FakeQueryNotFound()

    monkeypatch.setattr(fake_session, "query", mock_query)

    current_user = DummyUser(1, "commercial")

    updated_client, error = update_client(fake_session, 123, {}, current_user)

    assert updated_client is None
    assert "introuvable" in error


def test_update_client_not_authorized(monkeypatch, fake_session):
    client = Clients(id=1, first_name="Client", email="client@example.com", commercial_id=42)

    def mock_query(model):
        return FakeQueryUpdate(client)

    monkeypatch.setattr(fake_session, "query", mock_query)

    current_user = DummyUser(99, "commercial")

    updated_client, error = update_client(fake_session, 1, {}, current_user)

    assert updated_client is None
    assert "pas autorisé" in error


def test_update_client_email_already_used(monkeypatch, fake_session):
    client = Clients(id=1, email="old@example.com", commercial_id=42)
    other_client = Clients(id=2, email="new@example.com")

    def mock_query(model):
        class FakeQuery:
            def __init__(self):
                self.kwargs = None
            def filter_by(self, **kwargs):
                self.kwargs = kwargs
                return self
            def first(inner_self):
                if "id" in inner_self.kwargs:
                    return client
                elif "email" in inner_self.kwargs:
                    return other_client
                return None
        return FakeQuery()

    monkeypatch.setattr(fake_session, "query", mock_query)

    current_user = DummyUser(42, "commercial")
    updates = {"email": "new@example.com"}

    updated_client, error = update_client(fake_session, 1, updates, current_user)

    assert updated_client is None
    assert "déjà utilisé" in error



def test_update_client_exception(monkeypatch, fake_session):
    client = Clients(id=1, email="old@example.com", commercial_id=42)

    def mock_query(model):
        return FakeQueryUpdate(client)

    def failing_commit():
        raise Exception("DB crash")

    monkeypatch.setattr(fake_session, "query", mock_query)
    monkeypatch.setattr(fake_session, "commit", failing_commit)

    current_user = DummyUser(42, "commercial")
    updates = {"first_name": "Crash"}

    updated_client, error = update_client(fake_session, 1, updates, current_user)

    assert updated_client is None
    assert "Erreur inattendue" in error
    assert fake_session._rolled_back is True

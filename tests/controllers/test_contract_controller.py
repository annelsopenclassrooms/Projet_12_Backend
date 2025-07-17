import pytest
from app.controllers.contract_controller import create_contract, update_contract
from app.models import Contracts, Clients, Users

# === Mocks de session et modèles ===

class FakeQuery:
    def __init__(self, return_value):
        self.return_value = return_value

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self.return_value


class FakeSession:
    def __init__(self):
        self.added = None
        self.committed = False
        self.query_data = []

    def query(self, model):
        return FakeQuery(self.query_data.pop(0))

    def add(self, obj):
        obj.id = 999  # simule un ID auto-généré par la DB
        self.added = obj

    def commit(self):
        self.committed = True


class FakeUser:
    def __init__(self, id, role_name):
        self.id = id
        self.role = type("Role", (), {"name": role_name})

# === Fakes pour désactiver sentry_sdk ===

def fake_capture_message(*args, **kwargs):
    pass

def fake_capture_exception(*args, **kwargs):
    pass


# === Tests ===

def test_create_contract_success(monkeypatch):
    session = FakeSession()
    client = Clients(id=1)
    commercial = Users(id=2)
    commercial.role = type("Role", (), {"name": "commercial"})
    session.query_data = [client, commercial]

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = create_contract(session, client_id=1, commercial_id=2, total_amount=1000, amount_due=500)

    assert error is None
    assert contract.client_id == 1
    assert contract.commercial_id == 2
    assert contract.total_amount == 1000
    assert session.committed


def test_create_contract_client_not_found(monkeypatch):
    session = FakeSession()
    session.query_data = [None]  # client introuvable

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = create_contract(session, client_id=99, commercial_id=2, total_amount=1000, amount_due=500)

    assert contract is None
    assert error == "❌ Client ID 99 introuvable."


def test_create_contract_commercial_not_found(monkeypatch):
    session = FakeSession()
    client = Clients(id=1)
    session.query_data = [client, None]

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = create_contract(session, client_id=1, commercial_id=99, total_amount=1000, amount_due=500)

    assert contract is None
    assert error == "❌ Commercial ID 99 introuvable."


def test_create_contract_user_not_commercial(monkeypatch):
    session = FakeSession()
    client = Clients(id=1)
    user = Users(id=2)
    user.role = type("Role", (), {"name": "support"})
    session.query_data = [client, user]

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = create_contract(session, client_id=1, commercial_id=2, total_amount=1000, amount_due=500)

    assert contract is None
    assert error == "❌ L'utilisateur ID 2 n'est pas un commercial."


def test_create_contract_signed(monkeypatch):
    session = FakeSession()
    client = Clients(id=1)
    commercial = Users(id=2)
    commercial.role = type("Role", (), {"name": "commercial"})
    session.query_data = [client, commercial]

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = create_contract(
        session, client_id=1, commercial_id=2, total_amount=1000, amount_due=500, is_signed=True
    )

    assert contract is not None
    assert error is None
    assert contract.is_signed is True
    assert session.committed


def test_update_contract_success(monkeypatch):
    contract = Contracts(id=1, client_id=1, commercial_id=5, total_amount=1000)
    session = FakeSession()
    session.query_data = [contract]

    current_user = FakeUser(id=5, role_name="commercial")
    updates = {"total_amount": 1500}

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    updated, error = update_contract(session, contract_id=1, updates=updates, current_user=current_user)

    assert error is None
    assert updated.total_amount == 1500
    assert session.committed


def test_update_contract_not_found(monkeypatch):
    session = FakeSession()
    session.query_data = [None]

    current_user = FakeUser(id=1, role_name="gestion")

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = update_contract(session, contract_id=42, updates={}, current_user=current_user)

    assert contract is None
    assert error == "❌ Contrat avec l’ID 42 introuvable."


def test_update_contract_unauthorized(monkeypatch):
    contract = Contracts(id=1, commercial_id=2)
    session = FakeSession()
    session.query_data = [contract]

    current_user = FakeUser(id=3, role_name="commercial")

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    contract, error = update_contract(session, 1, {}, current_user)

    assert contract is None
    assert error == "⛔ Vous n’êtes pas autorisé à modifier ce contrat."


def test_update_contract_signed(monkeypatch):
    contract = Contracts(id=1, client_id=1, commercial_id=2)
    session = FakeSession()
    session.query_data = [contract]

    current_user = FakeUser(id=2, role_name="commercial")
    updates = {"is_signed": True}

    monkeypatch.setattr("app.controllers.contract_controller.sentry_sdk.capture_message", fake_capture_message)

    updated, error = update_contract(session, 1, updates, current_user)

    assert error is None
    assert updated.is_signed is True
    assert session.committed

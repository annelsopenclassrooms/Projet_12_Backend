import pytest
from app.controllers.event_controller import create_event, update_event
from app.models import Events, Clients, Contracts, Users


# === Fakes ===

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
        obj.id = 888  # simulate DB id
        self.added = obj

    def commit(self):
        self.committed = True


class FakeUser:
    def __init__(self, id, role_name):
        self.id = id
        self.role = type("Role", (), {"name": role_name})


# === Tests create_event ===

def test_create_event_success():
    session = FakeSession()
    session.query_data = [
        Clients(id=1),
        Contracts(id=2),
        Users(id=3, role=type("Role", (), {"name": "support"}))
    ]

    event, error = create_event(
        session,
        name="Conférence",
        contract_id=2,
        client_id=1,
        support_contact_id=3,
        date_start="2025-07-20",
        date_end="2025-07-21",
        location="Paris",
        attendees=100,
        notes="Tech event"
    )

    assert error is None
    assert event is not None
    assert session.committed
    assert event.name == "Conférence"
    assert event.support_contact_id == 3


def test_create_event_client_not_found():
    session = FakeSession()
    session.query_data = [None]  # client non trouvé

    event, error = create_event(
        session,
        name="Événement",
        contract_id=2,
        client_id=1,
        support_contact_id=3,
        date_start="2025-07-20",
        date_end="2025-07-21",
        location="Paris",
        attendees=50,
        notes="Note"
    )

    assert event is None
    assert error == "❌ Client ID 1 non trouvé."


def test_create_event_contract_not_found():
    session = FakeSession()
    session.query_data = [
        Clients(id=1),
        None  # contrat non trouvé
    ]

    event, error = create_event(
        session,
        name="Événement",
        contract_id=2,
        client_id=1,
        support_contact_id=3,
        date_start="2025-07-20",
        date_end="2025-07-21",
        location="Paris",
        attendees=50,
        notes="Note"
    )

    assert event is None
    assert error == "❌ Contract ID 2 non trouvé."


def test_create_event_invalid_support_contact():
    session = FakeSession()
    session.query_data = [
        Clients(id=1),
        Contracts(id=2),
        Users(id=3, role=type("Role", (), {"name": "gestion"}))  # mauvais rôle
    ]

    event, error = create_event(
        session,
        name="Événement",
        contract_id=2,
        client_id=1,
        support_contact_id=3,
        date_start="2025-07-20",
        date_end="2025-07-21",
        location="Paris",
        attendees=50,
        notes="Note"
    )

    assert event is None
    assert error == "❌ Support contact ID 3 invalide."


# === Tests update_event ===

def test_update_event_success_support():
    session = FakeSession()
    event = Events(id=1, name="Old Event", support_contact_id=3)
    session.query_data = [event]

    user = FakeUser(id=3, role_name="support")
    updates = {"name": "Updated Event", "attendees": 150}

    updated, error = update_event(session, event_id=1, updates=updates, current_user=user)

    assert error is None
    assert updated.name == "Updated Event"
    assert updated.attendees == 150
    assert session.committed


def test_update_event_success_gestion():
    session = FakeSession()
    event = Events(id=1, support_contact_id=3)
    session.query_data = [event]

    user = FakeUser(id=10, role_name="gestion")
    updates = {"support_contact_id": 99}

    updated, error = update_event(session, 1, updates, current_user=user)

    assert error is None
    assert updated.support_contact_id == 99


def test_update_event_unauthorized_support_other_event():
    session = FakeSession()
    event = Events(id=1, support_contact_id=2)  # support_contact ≠ current_user.id
    session.query_data = [event]

    user = FakeUser(id=3, role_name="support")  # essaye de modifier l'événement d'un autre

    updated, error = update_event(session, 1, {"name": "Hack"}, user)

    assert updated is None
    assert error == "⛔ Vous n'avez pas la permission de modifier cet événement."


def test_update_event_unauthorized_field_support():
    session = FakeSession()
    event = Events(id=1, support_contact_id=5)
    session.query_data = [event]

    user = FakeUser(id=5, role_name="support")
    updates = {"support_contact_id": 99}  # champ non autorisé

    updated, error = update_event(session, 1, updates, user)

    assert updated is None
    assert error == "⛔ Vous n'avez pas la permission de modifier 'support_contact_id' en tant que 'support'."


def test_update_event_not_found():
    session = FakeSession()
    session.query_data = [None]

    user = FakeUser(id=1, role_name="support")

    updated, error = update_event(session, 1, {}, user)

    assert updated is None
    assert error == "❌ Event ID 1 non trouvé."

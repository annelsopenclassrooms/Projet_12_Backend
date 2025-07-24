import sys
from unittest.mock import MagicMock

# Neutraliser les décorateurs AVANT l'import de event_view
if 'app.views.event_view' in sys.modules:
    del sys.modules['app.views.event_view']

mock_auth = MagicMock()
mock_auth.jwt_required = lambda f: f
mock_auth.role_required = lambda *roles: (lambda f: f)
sys.modules['app.utils.auth'] = mock_auth

import pytest
import app.views.event_view as event_view
from datetime import datetime, timedelta
from app.models import Clients, Contracts, Users, Events

# === Fakes ===

class FakeRole:
    def __init__(self, name):
        self.name = name

class FakeUser:
    def __init__(self, role_name="commercial"):
        self.id = 1
        self.first_name = "Jean"
        self.last_name = "Dupont"
        self.role = FakeRole(role_name)

# === Tests ===

def test_show_all_events_view(monkeypatch):
    fake_user = FakeUser("support")

    def fake_list_all_events(session):
        class FakeEvent:
            def __init__(self):
                self.id = 1
                self.name = "Conférence IA"
                self.client = type("Client", (), {"company_name": "OpenAI"})
                self.date_start = datetime(2025, 8, 10)
                self.date_end = datetime(2025, 8, 12)
                self.location = "Paris"
                self.attendees = 100
                self.support_contact = type("Support", (), {
                    "first_name": "Support",
                    "last_name": "User"
                })
        return [FakeEvent()]

    monkeypatch.setattr(event_view, "list_all_events", fake_list_all_events)
    event_view.show_all_events_view(fake_user)


def test_create_event_view(monkeypatch):
    fake_user = FakeUser("commercial")

    monkeypatch.setattr(event_view.Prompt, "ask", AskMock([
        "Nom de l'événement",
        "20/08/2025",
        "21/08/2025",
        "Lyon",
        "50",
        "Notes test"
    ]))
    monkeypatch.setattr(event_view, "safe_input_int", IntMock([1, 1, 1, 50]))
    monkeypatch.setattr(event_view, "safe_input_date", DateMock([
        datetime(2025, 8, 20), datetime(2025, 8, 21)
    ]))
    monkeypatch.setattr(event_view.Confirm, "ask", ConfirmMock([True]))

    monkeypatch.setattr(event_view, "SessionLocal", FakeSessionFactory(
        clients=[FakeClient(1)],
        contracts=[FakeContract(1)],
        support_users=[FakeSupportUser(1)]
    ))

    monkeypatch.setattr(event_view, "create_event", create_event_success)
    event_view.create_event_view(fake_user)


def test_filter_events_view(monkeypatch):
    fake_user = FakeUser("gestion")

    monkeypatch.setattr(event_view.Prompt, "ask", AskMock([
        "1",  # choix du filtre
        "1"   # ID de l’événement pour voir les détails
    ]))
    monkeypatch.setattr(event_view, "safe_input_int", IntMock([1]))
    monkeypatch.setattr(event_view.Confirm, "ask", ConfirmMock([True]))

    monkeypatch.setattr(event_view, "SessionLocal", FakeSessionFactory(
        events=[FakeEvent(1)]
    ))

    event_view.filter_events_view(fake_user)


# === Helpers ===

class AskMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index]
        self.index += 1
        return res

class IntMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index]
        self.index += 1
        return res

class DateMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index]
        self.index += 1
        return res

class ConfirmMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    def __call__(self, *args, **kwargs):
        res = self.responses[self.index]
        self.index += 1
        return res

class FakeClient:
    def __init__(self, id):
        self.id = id
        self.first_name = "Alice"
        self.last_name = "Durand"
        self.company_name = "DurandCorp"

class FakeContract:
    def __init__(self, id):
        self.id = id
        self.total_amount = 1000.0
        self.date_created = datetime(2024, 5, 1)

class FakeSupportUser:
    def __init__(self, id):
        self.id = id
        self.first_name = "Support"
        self.last_name = "User"

class FakeEvent:
    def __init__(self, id):
        self.id = id
        self.name = "Événement Test"
        self.client = type("Client", (), {"company_name": "DurandCorp"})
        self.date_start = datetime.now() + timedelta(days=1)
        self.date_end = datetime.now() + timedelta(days=2)
        self.support_contact = type("User", (), {"first_name": "Bob", "last_name": "Dupuis"})
        self.attendees = 100
        self.location = "Lyon"
        self.notes = "Événement fictif"

class FakeSession:
    def __init__(self, clients=None, contracts=None, support_users=None, events=None):
        self.clients = clients or []
        self.contracts = contracts or []
        self.support_users = support_users or []
        self.events = events or []

    def query(self, model):
        if model == Clients:
            return FakeQuery(self.clients)
        if model == Contracts:
            return FakeQuery(self.contracts)
        if model == Users:
            return FakeQuery(self.support_users)
        if model == Events:
            return FakeQuery(self.events)
        return FakeQuery([])

    def close(self):
        pass

class FakeQuery:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def get(self, id):
        return next((item for item in self.items if item.id == id), None)

class FakeSessionFactory:
    def __init__(self, clients=None, contracts=None, support_users=None, events=None):
        self.session = FakeSession(clients, contracts, support_users, events)
    def __call__(self):
        return self.session

def create_event_success(session, **kwargs):
    class Event:
        id = 42
    return Event(), None

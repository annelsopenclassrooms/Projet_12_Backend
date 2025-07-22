# tests/conftest.py

import pytest


# === Rôles et utilisateurs ===

class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeUser:
    def __init__(self, role_name="commercial", user_id=1, name="Alice", lastname="Martin"):
        self.id = user_id
        self.first_name = name
        self.last_name = lastname
        self.email = f"{name.lower()}@test.com"
        self.role = FakeRole(role_name)
        self.department = role_name


@pytest.fixture
def commercial_user():
    return FakeUser(role_name="commercial")


@pytest.fixture
def support_user():
    return FakeUser(role_name="support")


@pytest.fixture
def manager_user():
    return FakeUser(role_name="gestion")


# === Clients et contrats ===

class FakeClient:
    def __init__(self, first_name="Jean", last_name="Client", commercial=None):
        self.first_name = first_name
        self.last_name = last_name
        self.commercial = commercial or FakeUser()
        self.commercial_id = self.commercial.id


class FakeContract:
    def __init__(self, id, client, total_amount=1000.0, amount_due=500.0, is_signed=False):
        self.id = id
        self.client = client
        self.total_amount = total_amount
        self.amount_due = amount_due
        self.is_signed = is_signed
        self.date_created = __import__("datetime").datetime.now()


@pytest.fixture
def fake_contracts(commercial_user):
    return [
        FakeContract(1, FakeClient("Jean", commercial=commercial_user)),
        FakeContract(2, FakeClient("Marie", commercial=commercial_user)),
    ]


# === Faux ORM SQLAlchemy (Session, Query) ===

class FakeQuery:
    def __init__(self, contracts):
        self.contracts = contracts

    def all(self):
        return self.contracts

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def get(self, contract_id):
        for c in self.contracts:
            if c.id == contract_id:
                return c
        return None


class FakeSession:
    def __init__(self, contracts):
        self._contracts = contracts

    def query(self, model):
        return FakeQuery(self._contracts)

    def commit(self): pass
    def close(self): pass


def fake_session_factory(contracts):
    def _factory():
        return FakeSession(contracts)
    return _factory


# === Utilitaires ===

def fake_confirm_ask(message, default=False):
    return True


def fake_console_print(*args, **kwargs):
    pass


def fake_safe_input_float_factory(values):
    iterator = iter(values)
    def _float(prompt, default=None):
        return next(iterator)
    return _float


def fake_safe_input_int(prompt):
    return 1  # ID du contrat à modifier


def fake_update_contract(session, contract_id, updates, user):
    for c in session._contracts:
        if c.id == contract_id:
            c.total_amount = updates.get("total_amount", c.total_amount)
            c.amount_due = updates.get("amount_due", c.amount_due)
            c.is_signed = updates.get("is_signed", c.is_signed)
            return c, None
    return None, "Contract not found"

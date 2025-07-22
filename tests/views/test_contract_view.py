import pytest
import app.views.contract_view as contract_view_module
from app.views.contract_view import update_contract_view


# === Fakes ===

class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeUser:
    def __init__(self, user_id=1, name="Alice", lastname="Martin", role="commercial"):
        self.id = user_id
        self.first_name = name
        self.last_name = lastname
        self.email = f"{name.lower()}@test.com"
        self.role = FakeRole(role)


class FakeClient:
    def __init__(self, first_name="Jean", last_name="Client", commercial=None):
        self.first_name = first_name
        self.last_name = last_name
        self.commercial = commercial or FakeUser()


class FakeContract:
    def __init__(self, id, client, total_amount=1000.0, amount_due=500.0, is_signed=False):
        self.id = id
        self.client = client
        self.total_amount = total_amount
        self.amount_due = amount_due
        self.is_signed = is_signed
        self.date_created = __import__("datetime").datetime.now()


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


# === Fixtures et helpers ===

@pytest.fixture
def fake_contracts():
    user = FakeUser()
    return [
        FakeContract(1, FakeClient("Jean", commercial=user)),
        FakeContract(2, FakeClient("Marie", commercial=user)),
    ]


def fake_session_factory(contracts):
    def _factory():
        return FakeSession(contracts)
    return _factory


def fake_confirm_ask(message, default=False):
    # Toujours confirmer (oui)
    return True


def fake_console_print(*args, **kwargs):
    # Supprimer affichage console durant test
    pass


def fake_safe_input_float_factory(values):
    iterator = iter(values)
    def _float(prompt, default=None):
        return next(iterator)
    return _float


def fake_safe_input_int(prompt):
    # ID du contrat à modifier (toujours 1)
    return 1


def fake_update_contract(session, contract_id, updates, user):
    for c in session._contracts:
        if c.id == contract_id:
            c.total_amount = updates.get("total_amount", c.total_amount)
            c.amount_due = updates.get("amount_due", c.amount_due)
            c.is_signed = updates.get("is_signed", c.is_signed)
            return c, None
    return None, "Contract not found"


# === Test principal ===

def test_update_contract_view(monkeypatch, fake_contracts):
    selected_contract = fake_contracts[0]
    fake_user = FakeUser()

    # Monkeypatch via le module importé
    monkeypatch.setattr(contract_view_module, "SessionLocal", fake_session_factory(fake_contracts))
    monkeypatch.setattr(contract_view_module.Confirm, "ask", fake_confirm_ask)
    monkeypatch.setattr(contract_view_module.Console, "print", fake_console_print)
    monkeypatch.setattr(contract_view_module.helpers, "safe_input_float", fake_safe_input_float_factory([1500.0, 300.0]))
    monkeypatch.setattr(contract_view_module.helpers, "safe_input_int", fake_safe_input_int)
    monkeypatch.setattr(contract_view_module, "update_contract", fake_update_contract)

    # Appel de la vue
    update_contract_view(fake_user)

    # Assertions : vérifie les modifications
    assert selected_contract.total_amount == 1500.0
    assert selected_contract.amount_due == 300.0
    assert selected_contract.is_signed is True

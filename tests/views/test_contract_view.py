import pytest
from app.views import contract_view as contract_view_module

# ======= FAKE CLASSES =======
class FakeRole:
    def __init__(self, name="commercial"):
        self.name = name

class FakeUser:
    def __init__(self, id=1, first_name="Fabrice", last_name="User", role=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.role = role or FakeRole()

class FakeClient:
    def __init__(self, first_name="Jean", last_name="Client", commercial=None):
        self.first_name = first_name
        self.last_name = last_name
        self.commercial = commercial or FakeUser()
        self.commercial_id = self.commercial.id

class FakeContract:
    def __init__(self, contract_id, client, total_amount=1000.0, amount_due=200.0):
        self.id = contract_id
        self.client = client
        self.total_amount = total_amount
        self.amount_due = amount_due
        self.is_signed = False

# ======= FAKE HELPERS =======
def fake_confirm_ask(prompt="", default=False):
    return True  # On force la confirmation

def fake_console_print(*args, **kwargs):
    return None  # On ignore les prints

def fake_safe_input_float_factory(values):
    def fake_safe_input_float(*args, **kwargs):
        return values.pop(0)
    return fake_safe_input_float

def fake_safe_input_int(prompt, default=None):
    return 1

def fake_update_contract(session, contract_id, updates, current_user):
    # On récupère le contrat
    contract = next((c for c in session.contracts if c.id == contract_id), None)
    if not contract:
        return None, "Contract not found"

    # Mise à jour des champs
    contract.total_amount = updates.get("total_amount", contract.total_amount)
    contract.amount_due = updates.get("amount_due", contract.amount_due)
    contract.is_signed = updates.get("is_signed", contract.is_signed)

    return contract, None  # <-- 2 valeurs


# ======= FAKE SESSION =======
class FakeQuery:
    def __init__(self, data):
        self.data = data

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def all(self):
        return self.data

    def first(self):
        return self.data[0] if self.data else None

    def get(self, contract_id):
        return next((obj for obj in self.data if getattr(obj, "id", None) == contract_id), None)

class FakeSession:
    def __init__(self, contracts):
        self.contracts = contracts

    def query(self, *args, **kwargs):
        return FakeQuery(self.contracts)

    def commit(self):
        return None

    def close(self):
        return None

def fake_session_factory(fake_contracts):
    def fake_session():
        return FakeSession(fake_contracts)
    return fake_session

# ======= TESTS =======
def test_update_contract_view(monkeypatch):
    fake_user = FakeUser()
    fake_contracts = [FakeContract(1, FakeClient("Jean", commercial=fake_user))]

    # Patch auth
    monkeypatch.setattr("app.utils.auth.get_current_user", lambda: fake_user)

    # Patch session
    monkeypatch.setattr(contract_view_module, "SessionLocal", fake_session_factory(fake_contracts))

    # Patch Confirm.ask
    monkeypatch.setattr(
        contract_view_module,
        "Confirm",
        type("FakeConfirm", (), {"ask": staticmethod(fake_confirm_ask)})
    )

    # Patch console.print
    monkeypatch.setattr(contract_view_module.Console, "print", fake_console_print)

    # Patch inputs
    monkeypatch.setattr(
        contract_view_module.helpers,
        "safe_input_float",
        fake_safe_input_float_factory([1500.0, 300.0])
    )
    monkeypatch.setattr(contract_view_module.helpers, "safe_input_int", fake_safe_input_int)

    # Patch update_contract
    monkeypatch.setattr(contract_view_module, "update_contract", fake_update_contract)

    # Exécution
    contract_view_module.update_contract_view(fake_user)

    # Vérification
    selected_contract = fake_contracts[0]
    assert selected_contract.total_amount == 1500.0
    assert selected_contract.amount_due == 300.0

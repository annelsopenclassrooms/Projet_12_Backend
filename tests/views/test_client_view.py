import sys
from unittest.mock import MagicMock

# D'abord s'assurer que pytest ne charge pas le module avant qu'on neutralise
if 'app.views.client_view' in sys.modules:
    del sys.modules['app.views.client_view']

# Neutraliser les décorateurs dans app.utils.auth
mock_auth = MagicMock()
mock_auth.jwt_required = lambda f: f
mock_auth.role_required = lambda *roles: (lambda f: f)
sys.modules['app.utils.auth'] = mock_auth

import pytest
import app.views.client_view as cv


# Raccourcis
show_all_clients_view = cv.show_all_clients_view
create_client_view = cv.create_client_view
update_client_view = cv.update_client_view

class FakeUser:
    id = 1
    first_name = "Alice"

class FakeClient:
    id = 1
    first_name = "Jean"
    last_name = "Dupont"
    email = "jean@client.com"
    phone = "0600000000"
    company_name = "TestCorp"
    commercial_id = 1

@pytest.fixture
def fake_user():
    return FakeUser()

@pytest.fixture
def fake_session(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(cv, "SessionLocal", lambda: session)
    return session

# ---- TESTS ----

def test_show_all_clients_view_empty(monkeypatch, fake_session, fake_user):
    monkeypatch.setattr(cv, "list_all_clients", lambda s: [])
    show_all_clients_view(fake_user)

def test_show_all_clients_view_ok(monkeypatch, fake_session, fake_user):
    monkeypatch.setattr(cv, "list_all_clients", lambda s: [FakeClient()])
    show_all_clients_view(fake_user)

def test_create_client_view_ok(monkeypatch, fake_session, fake_user):
    monkeypatch.setattr(cv.Prompt, "ask", lambda msg, **k: "val")
    monkeypatch.setattr(cv, "safe_input_email", lambda msg: "mail@test.com")
    monkeypatch.setattr(cv, "create_client", lambda s, **k: (FakeClient(), None))
    create_client_view(fake_user)

def test_update_client_view_success(monkeypatch, fake_session, fake_user):
    c = FakeClient()
    fake_session.query().filter_by().all.return_value = [c]
    fake_session.query().filter_by().first.return_value = c
    monkeypatch.setattr(cv, "safe_input_int", lambda msg: 1)
    monkeypatch.setattr(cv.Prompt, "ask", lambda m, **k: "val")
    monkeypatch.setattr(cv, "safe_input_email", lambda m, default=None: "x@x.com")
    monkeypatch.setattr(cv, "safe_input_phone", lambda m, default=None: "0700000000")
    monkeypatch.setattr(cv.Confirm, "ask", lambda m, default=False: True)
    monkeypatch.setattr(cv, "update_client", lambda s, cid, u, cu: (c, None))
    update_client_view(fake_user)

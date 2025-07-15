import pytest
from unittest.mock import MagicMock
from app.menus import commercial_menu as menu


# === FAKE USERS ===
class FakeUser:
    def __init__(self, role_name, user_id=99):
        self.role = type("Role", (), {"name": role_name})
        self.id = user_id
        self.department = role_name


@pytest.fixture
def commercial_user():
    return FakeUser("commercial")


@pytest.fixture
def support_user():
    return FakeUser("support")


# === TEST MENU PRINCIPAL ===
def test_commercial_menu_quit(monkeypatch, commercial_user):
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: "0")
    monkeypatch.setattr("app.menus.commercial_menu.console.print", lambda *a, **k: None)

    result = menu.commercial_menu(commercial_user)
    assert result is None


# === TEST MENU CLIENTS ===
def test_commercial_clients_menu(monkeypatch, commercial_user):
    actions = iter(["1", "2", "3", "0"])
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: next(actions))

    called = []

    def make_mock(action_name):
        def _mock(user):
            called.append(action_name)
        return _mock

    monkeypatch.setattr("app.menus.commercial_menu.create_client_view", make_mock("create"))
    monkeypatch.setattr("app.menus.commercial_menu.update_client_view", make_mock("update"))
    monkeypatch.setattr("app.menus.commercial_menu.show_all_clients_view", make_mock("list"))

    menu.commercial_clients_menu(commercial_user)
    assert called == ["create", "update", "list"]


# === TEST MENU CONTRATS ===
def test_commercial_contrats_menu(monkeypatch, commercial_user):
    actions = iter(["1", "2", "3", "0"])
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: next(actions))

    called = []

    def mock_action(user):
        called.append(user.id)

    monkeypatch.setattr("app.menus.commercial_menu.update_contract_view", mock_action)
    monkeypatch.setattr("app.menus.commercial_menu.filter_contracts_view", mock_action)
    monkeypatch.setattr("app.menus.commercial_menu.show_all_contracts_view", mock_action)

    menu.commercial_contrats_menu(commercial_user)
    assert called == [commercial_user.id] * 3


# === TEST MENU EVENEMENTS ===
def test_commercial_events_menu(monkeypatch, commercial_user):
    actions = iter(["1", "2", "0"])
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: next(actions))

    called = []

    def mock_action(user):
        called.append(user.role.name)

    monkeypatch.setattr("app.menus.commercial_menu.create_event_view", mock_action)
    monkeypatch.setattr("app.menus.commercial_menu.show_all_events_view", mock_action)

    menu.commercial_evenements_menu(commercial_user)
    assert called == ["commercial", "commercial"]


# === TEST SÉCURITÉ RÔLE ===
def test_access_denied_to_non_commercial(monkeypatch, support_user):
    monkeypatch.setattr("app.menus.commercial_menu.console.print", lambda *a, **k: None)
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: "0")

    result = menu.commercial_menu(support_user)
    assert result is None


# === TEST DÉCORATEURS PRÉSENTS ===
def test_menus_are_protected_by_role_decorator():
    from app.menus.commercial_menu import (
        commercial_clients_menu,
        commercial_contrats_menu,
        commercial_evenements_menu
    )

    assert hasattr(commercial_clients_menu, "__wrapped__")
    assert hasattr(commercial_contrats_menu, "__wrapped__")
    assert hasattr(commercial_evenements_menu, "__wrapped__")


# === TEST display_action_menu SÉPARÉMENT ===
def test_display_action_menu(monkeypatch, commercial_user):
    from app.menus.commercial_menu import display_action_menu

    calls = []

    def test_view(user):
        calls.append("called")

    inputs = iter(["1", "0"])
    monkeypatch.setattr("app.menus.commercial_menu.Prompt.ask", lambda *a, **k: next(inputs))
    monkeypatch.setattr("app.menus.commercial_menu.console.print", lambda *a, **k: None)

    display_action_menu([
        ("1", "Test", test_view),
        ("0", "Quitter", None)
    ], commercial_user)

    assert calls == ["called"]

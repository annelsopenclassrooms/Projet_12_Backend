import pytest
from app.menus import gestion_menu as menu


# === Fake user avec rôle ===
class FakeUser:
    def __init__(self, role_name="gestion", user_id=1):
        self.role = type("Role", (), {"name": role_name})
        self.id = user_id


# === Fixtures ===
@pytest.fixture
def gestion_user():
    return FakeUser("gestion")

@pytest.fixture
def support_user():
    return FakeUser("support")


# === Helpers ===

# Simule Prompt.ask avec une séquence d'entrées
def mock_prompt_ask_sequence(monkeypatch, inputs):
    it = iter(inputs)

    def mock_prompt(*args, **kwargs):
        return next(it)

    monkeypatch.setattr("app.menus.gestion_menu.Prompt.ask", mock_prompt)

# Ne rien afficher sur console.print (rich)
def mock_console_print(*args, **kwargs):
    pass

# Crée une fonction mockée qui loggue son appel
def mock_and_track(monkeypatch, target_module, attr_name, label, tracker):
    def mocked_func(*args, **kwargs):
        tracker.append(label)
    monkeypatch.setattr(target_module, attr_name, mocked_func)


# === TEST : Menu principal ===
def test_gestion_main_menu_quit(monkeypatch, gestion_user):
    mock_prompt_ask_sequence(monkeypatch, ["0"])
    monkeypatch.setattr("app.menus.gestion_menu.console.print", mock_console_print)

    result = menu.gestion_main_menu(gestion_user)
    assert result is None


# === TEST : collaborateurs_menu ===
def test_collaborateurs_menu(monkeypatch, gestion_user):
    calls = []
    mock_prompt_ask_sequence(monkeypatch, ["1", "2", "3", "4", "0"])

    mock_and_track(monkeypatch, menu, "create_user_view", "create", calls)
    mock_and_track(monkeypatch, menu, "update_user_view", "update", calls)
    mock_and_track(monkeypatch, menu, "delete_user_view", "delete", calls)
    mock_and_track(monkeypatch, menu, "show_all_users_view", "list", calls)

    menu.collaborateurs_menu(gestion_user)
    assert calls == ["create", "update", "delete", "list"]


# === TEST : clients_menu ===
def test_clients_menu(monkeypatch, gestion_user):
    calls = []
    mock_prompt_ask_sequence(monkeypatch, ["1", "0"])

    mock_and_track(monkeypatch, menu, "show_all_clients_view", "list_clients", calls)

    menu.clients_menu(gestion_user)
    assert calls == ["list_clients"]


# === TEST : contrats_menu ===
def test_contrats_menu(monkeypatch, gestion_user):
    calls = []
    mock_prompt_ask_sequence(monkeypatch, ["1", "2", "3", "0"])

    mock_and_track(monkeypatch, menu, "create_contract_view", "create", calls)
    mock_and_track(monkeypatch, menu, "update_contract_view", "update", calls)
    mock_and_track(monkeypatch, menu, "show_all_contracts_view", "list", calls)

    menu.contrats_menu(gestion_user)
    assert calls == ["create", "update", "list"]


# === TEST : evenements_menu ===
def test_evenements_menu(monkeypatch, gestion_user):
    calls = []
    mock_prompt_ask_sequence(monkeypatch, ["1", "2", "3", "0"])

    mock_and_track(monkeypatch, menu, "update_event_view", "update", calls)
    mock_and_track(monkeypatch, menu, "show_all_events_view", "list", calls)
    mock_and_track(monkeypatch, menu, "filter_events_view", "filter", calls)

    menu.evenements_menu(gestion_user)
    assert calls == ["update", "list", "filter"]


# === TEST : refus d'accès pour utilisateur non gestionnaire ===
def test_access_denied_for_non_gestion(support_user):
    result = menu.gestion_main_menu(support_user)
    assert result is None

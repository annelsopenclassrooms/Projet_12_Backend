import pytest
from app.menus import support_menu


class FakeUser:
    def __init__(self, first_name="Bob", role_name="support"):
        self.first_name = first_name
        self.role = type("Role", (), {"name": role_name})


@pytest.mark.parametrize(
    "input_choice, expected_func_name",
    [
        ("1", "show_all_clients_view"),
        ("2", "show_all_contracts_view"),
        ("3", "show_all_events_view"),
        ("4", "filter_events_view"),
        ("5", "show_user_events_view"),
        ("6", "update_event_view"),
    ]
)
def test_support_menu(monkeypatch, input_choice, expected_func_name):
    called = []

    # Patch des vues support
    monkeypatch.setattr(support_menu, "show_all_clients_view", lambda user: called.append("show_all_clients_view"))
    monkeypatch.setattr(support_menu, "show_all_contracts_view", lambda user: called.append("show_all_contracts_view"))
    monkeypatch.setattr(support_menu, "show_all_events_view", lambda user: called.append("show_all_events_view"))
    monkeypatch.setattr(support_menu, "filter_events_view", lambda user: called.append("filter_events_view"))
    monkeypatch.setattr(support_menu, "update_event_view", lambda user: called.append("update_event_view"))
    monkeypatch.setattr(support_menu, "show_user_events_view", lambda user: called.append("show_user_events_view"))

    # Patch du display_action_menu pour simuler le choix utilisateur
    def fake_display_action_menu(actions, user):
        for key, _, func in actions:
            if key == input_choice and func:
                func(user)

    monkeypatch.setattr(support_menu, "display_action_menu", fake_display_action_menu)

    # Appel du menu
    support_menu.support_menu(FakeUser())

    assert called == [expected_func_name]


def test_support_menu_exit(monkeypatch):
    called = []

    # Patch toutes les vues (aucune ne devrait être appelée)
    monkeypatch.setattr(support_menu, "show_all_clients_view", lambda user: called.append("clients"))
    monkeypatch.setattr(support_menu, "show_all_contracts_view", lambda user: called.append("contracts"))
    monkeypatch.setattr(support_menu, "show_all_events_view", lambda user: called.append("events"))
    monkeypatch.setattr(support_menu, "filter_events_view", lambda user: called.append("filter"))
    monkeypatch.setattr(support_menu, "update_event_view", lambda user: called.append("update"))

    # Simule le choix "0" (quitter)
    def fake_display_action_menu(actions, user):
        for key, _, func in actions:
            if key == "0":
                return  # Pas d'appel à une fonction

    monkeypatch.setattr(support_menu, "display_action_menu", fake_display_action_menu)

    support_menu.support_menu(FakeUser())

    assert called == []  # Aucune vue ne doit être appelée

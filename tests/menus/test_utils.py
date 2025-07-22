import pytest
from unittest.mock import MagicMock
import app.menus.utils as mu


def test_safe_prompt_ask(monkeypatch):
    # Cas normal
    monkeypatch.setattr(mu.Prompt, "ask", lambda *a, **k: "1")
    assert mu.safe_prompt_ask("Choix ?", ["1", "2"]) == "1"

    # Cas OSError
    def raise_oserror(*a, **k):
        raise OSError
    monkeypatch.setattr(mu.Prompt, "ask", raise_oserror)
    assert mu.safe_prompt_ask("Choix ?", ["1", "2"], default="0") == "0"


def test_safe_input(monkeypatch):
    # Cas normal
    monkeypatch.setattr("builtins.input", lambda msg="": None)
    mu.safe_input("Test ?")

    # Cas OSError
    def raise_oserror(msg=""):
        raise OSError
    monkeypatch.setattr("builtins.input", raise_oserror)
    mu.safe_input("Test ?")

def test_display_action_menu(monkeypatch):
    import app.menus.utils as mu

    calls = []

    def action_no_args():
        calls.append("no_args")

    # On simule le choix de l'action puis sortie
    responses = ["1", "0"]

    def mock_safe_prompt_ask(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(mu, "safe_prompt_ask", mock_safe_prompt_ask)
    monkeypatch.setattr(mu, "safe_input", lambda *a, **k: None)

    actions = [("1", "Action test", action_no_args)]
    mu.display_action_menu(actions, user="TestUser")

    assert "no_args" in calls

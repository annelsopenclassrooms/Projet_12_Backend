import pytest
import app.views.logout as logout_view

def test_logout_when_token_exists(monkeypatch, capsys):
    called = {"removed": False}

    def fake_exists(path):
        return path == ".token"

    def fake_remove(path):
        if path == ".token":
            called["removed"] = True

    monkeypatch.setattr("os.path.exists", fake_exists)
    monkeypatch.setattr("os.remove", fake_remove)

    logout_view.logout()

    out = capsys.readouterr().out
    assert "✅ Déconnexion réussie." in out
    assert called["removed"] is True


def test_logout_when_token_missing(monkeypatch, capsys):
    monkeypatch.setattr("os.path.exists", lambda path: False)

    logout_view.logout()

    out = capsys.readouterr().out
    assert "ℹ️ Aucun utilisateur connecté." in out

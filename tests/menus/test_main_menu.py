import pytest
from app.menus import main_menu


class FakeUser:
    def __init__(self, role_name="gestion", first_name="Alice"):
        self.role = type("Role", (), {"name": role_name})
        self.first_name = first_name


@pytest.fixture
def gestion_user():
    return FakeUser("gestion")

@pytest.fixture
def commercial_user():
    return FakeUser("commercial")

@pytest.fixture
def support_user():
    return FakeUser("support")

@pytest.fixture
def unknown_user():
    return FakeUser("unknown")


def test_main_menu_gestion(monkeypatch, gestion_user):
    called = {}

    def mock_gestion(user):
        called["gestion"] = True

    monkeypatch.setattr(main_menu, "gestion_main_menu", mock_gestion)

    main_menu.main_menu(gestion_user)
    assert called.get("gestion") is True


def test_main_menu_commercial(monkeypatch, commercial_user):
    called = {}

    def mock_commercial(user):
        called["commercial"] = True

    monkeypatch.setattr(main_menu, "commercial_menu", mock_commercial)

    main_menu.main_menu(commercial_user)
    assert called.get("commercial") is True


def test_main_menu_support(monkeypatch, support_user):
    called = {}

    def mock_support(user):
        called["support"] = True

    monkeypatch.setattr(main_menu, "support_menu", mock_support)

    main_menu.main_menu(support_user)
    assert called.get("support") is True


def test_main_menu_unknown_role(monkeypatch, unknown_user, capsys):
    # Ne patch rien ici : doit afficher une erreur
    main_menu.main_menu(unknown_user)

    captured = capsys.readouterr()
    assert "❌ Rôle inconnu" in captured.out

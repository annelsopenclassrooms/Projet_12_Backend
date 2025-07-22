import builtins
import pytest
from datetime import date
from app.utils import helpers


# Helper pour simuler input
def set_input(monkeypatch, inputs):
    """
    Simule plusieurs inputs successifs avec une liste.
    """
    iterator = iter(inputs)
    monkeypatch.setattr(builtins, "input", lambda _: next(iterator))


# ======= Tests safe_input_int ======= #
def test_safe_input_int_valid(monkeypatch):
    set_input(monkeypatch, ["42"])
    result = helpers.safe_input_int("Enter number: ")
    assert result == 42


def test_safe_input_int_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["abc", "10"])
    result = helpers.safe_input_int("Enter number: ")
    captured = capsys.readouterr()
    assert "❌ Please enter a valid number." in captured.out
    assert result == 10


def test_safe_input_int_allow_empty(monkeypatch):
    set_input(monkeypatch, [""])
    result = helpers.safe_input_int("Enter number: ", allow_empty=True)
    assert result is None


# ======= Tests safe_input_float ======= #
def test_safe_input_float_valid(monkeypatch):
    set_input(monkeypatch, ["3.14"])
    result = helpers.safe_input_float("Enter float: ")
    assert result == 3.14


def test_safe_input_float_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["x", "2.5"])
    result = helpers.safe_input_float("Enter float: ")
    captured = capsys.readouterr()
    assert "❌ Please enter a valid number." in captured.out
    assert result == 2.5


# ======= Tests safe_input_yes_no ======= #
@pytest.mark.parametrize("inp, expected", [
    ("y", True),
    ("yes", True),
    ("o", True),
    ("oui", True),
    ("n", False),
    ("no", False),
    ("non", False),
])
def test_safe_input_yes_no_valid(monkeypatch, inp, expected):
    set_input(monkeypatch, [inp])
    assert helpers.safe_input_yes_no("Continue? ") == expected


def test_safe_input_yes_no_default(monkeypatch):
    set_input(monkeypatch, [""])
    assert helpers.safe_input_yes_no("Continue? ", default=True) is True


def test_safe_input_yes_no_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["maybe", "y"])
    result = helpers.safe_input_yes_no("Continue? ")
    captured = capsys.readouterr()
    assert "❌ Please answer y/n." in captured.out
    assert result is True


# ======= Tests safe_input_date ======= #
def test_safe_input_date_valid(monkeypatch):
    set_input(monkeypatch, ["2025-01-01"])
    result = helpers.safe_input_date("Enter date: ")
    assert result == date(2025, 1, 1)


def test_safe_input_date_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["bad-date", "2024-12-31"])
    result = helpers.safe_input_date("Enter date: ")
    captured = capsys.readouterr()
    assert "❌ Please enter a valid date" in captured.out
    assert result == date(2024, 12, 31)


def test_safe_input_date_allow_empty(monkeypatch):
    set_input(monkeypatch, [""])
    result = helpers.safe_input_date("Enter date: ", allow_empty=True)
    assert result is None


# ======= Tests safe_input_choice ======= #
def test_safe_input_choice_valid(monkeypatch):
    set_input(monkeypatch, ["2"])
    result = helpers.safe_input_choice("Choose", [1, 2, 3])
    assert result == 2


def test_safe_input_choice_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["5", "1"])
    result = helpers.safe_input_choice("Choose", [1, 2, 3])
    captured = capsys.readouterr()
    assert "❌ Please enter a valid choice" in captured.out
    assert result == 1


# ======= Tests safe_input_email ======= #
def test_safe_input_email_valid(monkeypatch):
    set_input(monkeypatch, ["test@example.com"])
    result = helpers.safe_input_email("Enter email: ")
    assert result == "test@example.com"


def test_safe_input_email_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["invalid-email", "user@domain.com"])
    result = helpers.safe_input_email("Enter email: ")
    captured = capsys.readouterr()
    assert "❌ Please enter a valid email." in captured.out
    assert result == "user@domain.com"


# ======= Tests safe_input_phone ======= #
def test_safe_input_phone_valid(monkeypatch):
    set_input(monkeypatch, ["+33 6 12 34 56 78"])
    result = helpers.safe_input_phone("Enter phone: ")
    assert result == "+33 6 12 34 56 78"


def test_safe_input_phone_invalid_then_valid(monkeypatch, capsys):
    set_input(monkeypatch, ["abcd", "0601020304"])
    result = helpers.safe_input_phone("Enter phone: ")
    captured = capsys.readouterr()
    assert "❌ Please enter a valid phone number." in captured.out
    assert result == "0601020304"

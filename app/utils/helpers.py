from datetime import datetime
import re


def safe_input_int(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("❌ Please enter a valid number.")


def safe_input_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("❌ Please enter a valid number.")


def safe_input_yes_no(prompt, default=False):
    while True:
        value = input(prompt).strip().lower()
        if not value:
            return default
        if value in ["y", "yes", "o", "oui"]:
            return True
        elif value in ["n", "no", "non"]:
            return False
        else:
            print("❌ Please answer y/n.")


def safe_input_date(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Please enter a valid date (YYYY-MM-DD).")


def safe_input_choice(prompt, choices):
    choices_str = [str(choice) for choice in choices]
    while True:
        value = input(f"{prompt} ({'/'.join(choices_str)}): ").strip()
        if value in choices_str:
            for c in choices:
                if str(c) == value:
                    return c
        print(f"❌ Please enter a valid choice: {', '.join(choices_str)}")


def safe_input_email(prompt):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    while True:
        value = input(prompt).strip()
        if re.match(pattern, value):
            return value
        print("❌ Please enter a valid email.")


def safe_input_phone(prompt):
    """
    Prompt for a valid phone number (simple check).
    Accepts digits, +, spaces, -.
    """
    pattern = r"^[\d +()-]{5,20}$"
    while True:
        value = input(prompt).strip()
        if re.match(pattern, value):
            return value
        print("❌ Please enter a valid phone number.")

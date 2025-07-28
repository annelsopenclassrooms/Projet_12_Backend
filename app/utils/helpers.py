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
            print("❌ Merci d'entrer un nombre valide.")


def safe_input_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("❌ Merci d'entrer un nombre valide.")


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


def safe_input_date(prompt, default=None, allow_empty=False):
    """
    Demande une date à l'utilisateur avec un format YYYY-MM-DD.
    - prompt : message affiché à l'utilisateur
    - default : valeur par défaut si aucune entrée n'est donnée
    - allow_empty : permet de retourner None si l'entrée est vide
    """
    while True:
        # Affiche le prompt avec la valeur par défaut entre crochets si elle existe
        message = f"{prompt} [{default}]: " if default else f"{prompt}: "
        value = input(message).strip()

        # Si l'utilisateur n'entre rien, utiliser la valeur par défaut
        if not value and default:
            return default

        # Si vide autorisé et rien entré, retourner None
        if allow_empty and not value:
            return None

        # Essayer de parser la date
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Veuillez entrer une date valide au format YYYY-MM-DD.")


def safe_input_choice(prompt, choices):
    choices_str = [str(choice) for choice in choices]
    while True:
        value = input(f"{prompt} ({'/'.join(choices_str)}): ").strip()
        if value in choices_str:
            for c in choices:
                if str(c) == value:
                    return c
        print(f"❌ M: {', '.join(choices_str)}")


def safe_input_email(prompt):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    while True:
        value = input(prompt).strip()
        if re.match(pattern, value):
            return value
        print("❌ Merci d'entrer un email valide.")


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
        print("❌ Merci d'entrer un numéro de téléphone valide.")

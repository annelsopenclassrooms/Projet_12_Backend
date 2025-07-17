from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from app.views.client_view import show_all_clients_view
from app.views.contract_view import create_contract_view, update_contract_view, show_all_contracts_view
from app.views.event_view import update_event_view, show_all_events_view, filter_events_view
from app.views.user_view import create_user_view, update_user_view, delete_user_view, show_all_users_view
from app.utils.auth import role_required

console = Console()

# Nouvelle fonction utilitaire pour éviter Prompt.ask en test
def safe_prompt_ask(prompt_text, choices, default="0"):
    try:
        return Prompt.ask(prompt_text, choices=choices, default=default)
    except OSError:
        # Retourne "0" automatiquement si on est en test sans stdin
        return "0"

# Menu principal
@role_required("gestion")
def gestion_main_menu(user):
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Section")

        sections = [
            ("1", "Collaborateurs"),
            ("2", "Clients"),
            ("3", "Contrats"),
            ("4", "Événements"),
            ("0", "[red]Quitter"),
        ]

        for choice, label in sections:
            table.add_row(choice, label)

        console.print(table)

        choice = safe_prompt_ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[s[0] for s in sections])

        if choice == "1":
            collaborateurs_menu(user)
        elif choice == "2":
            clients_menu(user)
        elif choice == "3":
            contrats_menu(user)
        elif choice == "4":
            evenements_menu(user)
        elif choice == "0":
            console.print("\n[bold red]À bientôt ![/bold red] 👋")
            break

# Affichage des menus avec actions
@role_required("gestion")
def collaborateurs_menu(user):
    actions = [
        ("1", "Créer un collaborateur", create_user_view),
        ("2", "Modifier un collaborateur", update_user_view),
        ("3", "Supprimer un collaborateur", delete_user_view),
        ("4", "Lister les collaborateurs", show_all_users_view),
        ("0", "[red]Retour", None),
    ]
    display_action_menu(actions, user)

@role_required("gestion")
def clients_menu(user):
    actions = [
        ("1", "Lister tous les clients", show_all_clients_view),
        ("0", "[red]Retour", None),
    ]
    display_action_menu(actions, user)

@role_required("gestion")
def contrats_menu(user):
    actions = [
        ("1", "Créer un contrat", create_contract_view),
        ("2", "Modifier un contrat", update_contract_view),
        ("3", "Lister tous les contrats", show_all_contracts_view),
        ("0", "[red]Retour", None),
    ]
    display_action_menu(actions, user)

@role_required("gestion")
def evenements_menu(user):
    actions = [
        ("1", "Modifier un événement (attribuer support)", update_event_view),
        ("2", "Lister tous les événements", show_all_events_view),
        ("3", "Filtrer les événements", filter_events_view),
        ("0", "[red]Retour", None),
    ]
    display_action_menu(actions, user)

# display_action_menu partagé
def display_action_menu(actions, user):
    while True:
        table = Table(title="Sélection d'action", header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")
        for choice, label, *_ in actions:
            table.add_row(choice, label)
        console.print(table)

        valid_choices = [a[0] for a in actions]
        choice = safe_prompt_ask("[bold cyan]Votre choix[/bold cyan]", choices=valid_choices)

        for action in actions:
            if action[0] == choice:
                if len(action) >= 3 and action[2]:
                    action[2](user)
                if action[0] == "0" or len(action) < 3 or not action[2]:
                    return


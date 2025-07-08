from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from app.views.client_view import show_all_clients_view
from app.views.contract_view import create_contract_view, update_contract_view, show_all_contracts_view
from app.views.event_view import update_event_view, show_all_events_view, filter_events_view
from app.views.user_view import create_user_view, update_user_view, delete_user_view, show_all_users_view
from app.utils.auth import role_required

from app.menus.utils import display_action_menu

console = Console()

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

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[s[0] for s in sections], default="0")

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

@role_required("gestion")
def collaborateurs_menu(user):
    actions = [
        ("1", "Créer un collaborateur", create_user_view),
        ("2", "Modifier un collaborateur", update_user_view),
        ("3", "Supprimer un collaborateur", delete_user_view),
        ("4", "Lister les collaborateurs", show_all_users_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)

@role_required("gestion")
def clients_menu(user):
    actions = [
        ("1", "Lister tous les clients", show_all_clients_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)

@role_required("gestion")
def contrats_menu(user):
    actions = [
        ("1", "Créer un contrat", create_contract_view),
        ("2", "Modifier un contrat", update_contract_view),
        ("3", "Lister tous les contrats", show_all_contracts_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)

@role_required("gestion")
def evenements_menu(user):
    actions = [
        ("1", "Modifier un événement (attribuer support)", update_event_view),
        ("2", "Lister tous les événements", show_all_events_view),
        ("3", "Filtrer les événements", filter_events_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)

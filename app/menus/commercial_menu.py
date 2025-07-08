from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


from app.utils.auth import role_required
from app.views.client_view import create_client_view, update_client_view, show_all_clients_view
from app.views.contract_view import update_contract_view, filter_contracts_view
from app.views.event_view import create_event_view

from app.menus.utils import display_action_menu

console = Console()

@role_required("commercial")
def commercial_menu(user):
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Section")

        sections = [
            ("1", "Clients"),
            ("2", "Contrats"),
            ("3", "Événements"),
            ("0", "[red]Quitter"),
        ]

        for choice, label in sections:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[s[0] for s in sections], default="0")

        if choice == "1":
            commercial_clients_menu(user)
        elif choice == "2":
            commercial_contrats_menu(user)
        elif choice == "3":
            commercial_evenements_menu(user)
        elif choice == "0":
            console.print("\n[bold red]À bientôt ![/bold red] 👋")
            break


# CLIENTS

@role_required("commercial")
def commercial_clients_menu(user):
    actions = [
        ("1", "Créer un client (associé automatiquement)", create_client_view),
        ("2", "Modifier un client (dont vous êtes responsable)", update_client_view),
        ("3", "Lister tous les clients", show_all_clients_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)



# CONTRATS

@role_required("commercial")
def commercial_contrats_menu(user):
    actions = [
        ("1", "Modifier un contrat (dont vous êtes responsable)", update_contract_view),
        ("2", "Filtrer les contrats (non signés / non payés)", filter_contracts_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)



# ÉVÉNEMENTS

@role_required("commercial")
def commercial_evenements_menu(user):
    actions = [
        ("1", "Créer un événement (client ayant signé)", create_event_view),
        ("0", "[red]Retour"),
    ]
    display_action_menu(actions)


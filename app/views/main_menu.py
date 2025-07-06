from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from app.views.client_view import create_client_view, update_client_view, show_all_clients_view
from app.views.contract_view import create_contract_view, update_contract_view, show_all_contracts_view
from app.views.event_view import update_event_view, show_all_events_view
from app.views.user_view import create_user_view, update_user_view, delete_user_view, show_all_users_view

from app.utils.auth import role_required
from app.views.event_view import filter_events_view

console = Console()


def main_menu(user):
    while True:
        console.clear()
        console.rule("[bold cyan]📌 CRM Epic Events")

        console.print(f"[bold green]Bienvenue [bold yellow]{user.first_name} ({user.role.name.upper()})[/bold yellow][/bold green]\n")

        if user.role.name == "gestion":
            gestion_main_menu(user)
        elif user.role.name == "commercial":
            commercial_menu(user)
        elif user.role.name == "support":
            support_menu(user)
        else:
            console.print("[red]❌ Rôle inconnu. Accès refusé.[/red]")
            break


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
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        actions = [
            ("1", "Créer un collaborateur", create_user_view),
            ("2", "Modifier un collaborateur", update_user_view),
            ("3", "Supprimer un collaborateur", delete_user_view),
            ("4", "Lister les collaborateurs", show_all_users_view),
            ("0", "[red]Retour"),
        ]

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[a[0] for a in actions], default="0")

        if choice == "0":
            break

        action = next((a[2] for a in actions if a[0] == choice), None)
        if action:
            action()
        else:
            console.print("[yellow]⚠️ Action non disponible[/yellow]")

        input("\nAppuyez sur Entrée pour continuer...")


@role_required("gestion")
def clients_menu(user):
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        actions = [
            ("1", "Lister tous les clients", show_all_clients_view),
            ("0", "[red]Retour"),
        ]

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[a[0] for a in actions], default="0")

        if choice == "0":
            break

        action = next((a[2] for a in actions if a[0] == choice), None)
        if action:
            action()
        else:
            console.print("[yellow]⚠️ Action non disponible[/yellow]")

        input("\nAppuyez sur Entrée pour continuer...")


@role_required("gestion")
def contrats_menu(user):
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        actions = [
            ("1", "Créer un contrat", create_contract_view),
            ("2", "Modifier un contrat", update_contract_view),
            ("3", "Lister tous les contrats", show_all_contracts_view),
            ("0", "[red]Retour"),
        ]

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[a[0] for a in actions], default="0")

        if choice == "0":
            break

        action = next((a[2] for a in actions if a[0] == choice), None)
        if action:
            action()
        else:
            console.print("[yellow]⚠️ Action non disponible[/yellow]")

        input("\nAppuyez sur Entrée pour continuer...")


@role_required("gestion")
def evenements_menu(user):
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        actions = [
            ("1", "Modifier un événement (attribuer support)", update_event_view),
            ("2", "Lister tous les événements", show_all_events_view),
            ("3", "Filtrer les événements", filter_events_view),
            ("0", "[red]Retour"),
        ]

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=[a[0] for a in actions], default="0")

        if choice == "0":
            break

        action = next((a[2] for a in actions if a[0] == choice), None)
        if action:
            action()
        else:
            console.print("[yellow]⚠️ Action non disponible[/yellow]")

        input("\nAppuyez sur Entrée pour continuer...")


@role_required("commercial")
def commercial_menu(user):
    console.print("[yellow]TODO : Menu commercial à implémenter[/yellow]")
    input("\nAppuyez sur Entrée pour continuer...")


@role_required("support")
def support_menu(user):
    console.print("[yellow]TODO : Menu support à implémenter[/yellow]")
    input("\nAppuyez sur Entrée pour continuer...")

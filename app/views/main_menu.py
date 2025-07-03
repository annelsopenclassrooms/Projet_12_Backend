from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from app.views.client_view import create_client_view, update_client_view
from app.views.contract_view import create_contract_view, update_contract_view
from app.views.event_view import update_event_view
from app.views.user_view import create_user_view, update_user_view, delete_user_view

console = Console()

def main_menu(user):
    while True:
        console.clear()
        console.rule("[bold cyan]📌 CRM Epic Events")

        console.print(f"[bold green]Bienvenue [bold yellow]{user.first_name} ({user.role.name.upper()})[/bold yellow][/bold green]\n")

        options = []

        if user.role.name == "gestion":
            options = [
                ("1", "Créer un collaborateur", create_user_view),
                ("2", "Modifier un collaborateur", update_user_view),
                ("3", "Supprimer un collaborateur", delete_user_view),
                ("4", "Créer un contrat", create_contract_view),
                ("5", "Modifier un contrat", update_contract_view),
                ("6", "Modifier un événement (attribuer support)", update_event_view),
            ]
        elif user.role.name == "commercial":
            options = [
                ("1", "Créer un client", create_client_view),
                ("2", "Modifier vos clients", update_client_view),
                ("3", "Modifier vos contrats", update_contract_view),
            ]
        elif user.role.name == "support":
            options = [
                ("1", "Filtrer vos événements", None),  # TODO
                ("2", "Modifier vos événements", update_event_view),
            ]
        else:
            console.print("[red]❌ Rôle inconnu. Accès refusé.[/red]")
            break

        options.append(("0", "[red]Quitter", None))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        for choice, label, _ in options:
            table.add_row(choice, label)

        console.print(table)

        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", default="0")

        # Chercher l'option sélectionnée
        selected_option = next((opt for opt in options if opt[0] == choice), None)

        if not selected_option:
            console.print("[red]❌ Choix invalide[/red]")
            input("Appuyez sur Entrée pour continuer...")
            continue

        # Décomposer l'option
        option_number, option_label, option_action = selected_option

        if choice == "0":
            console.print("\n[bold red]À bientôt ![/bold red] 👋")
            break

        if option_action:
            option_action()
        else:
            console.print("[yellow]⚠️ Fonction non encore implémentée[/yellow]")

        input("\nAppuyez sur Entrée pour continuer...")

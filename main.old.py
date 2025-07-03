# main.py
from app.views.login import login
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def gestion_menu(user):
    console.print("\n📋 [bold cyan]Menu Gestion[/bold cyan]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Créer/Modifier un contrat")
    table.add_row("2", "Gérer les événements (attribution support)")
    table.add_row("3", "Créer/Modifier un utilisateur")
    console.print(table)
    Prompt.ask("Choisissez une option")

def commercial_menu(user):
    console.print("\n📋 [bold green]Menu Commercial[/bold green]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Créer un client")
    table.add_row("2", "Modifier un client")
    table.add_row("3", "Gérer les contrats clients")
    table.add_row("4", "Créer un événement")
    console.print(table)
    Prompt.ask("Choisissez une option")

def support_menu(user):
    console.print("\n📋 [bold magenta]Menu Support[/bold magenta]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Voir mes événements")
    table.add_row("2", "Mettre à jour un événement")
    console.print(table)
    Prompt.ask("Choisissez une option")

def main():
    user = login()
    if not user:
        return

    role = user.role.name.lower()
    if role == "gestion":
        gestion_menu(user)
    elif role == "commercial":
        commercial_menu(user)
    elif role == "support":
        support_menu(user)
    else:
        console.print("⚠️ [bold red]Rôle non reconnu.[/bold red]")

if __name__ == "__main__":
    main()

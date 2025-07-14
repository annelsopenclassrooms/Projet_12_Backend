from rich.console import Console
from app.utils.auth import role_required
from app.menus.gestion_menu import gestion_main_menu
from app.menus.commercial_menu import commercial_menu
import sentry_sdk

console = Console()


def main_menu(user):


    
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

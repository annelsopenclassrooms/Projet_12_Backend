from rich.console import Console
from app.utils.auth import role_required

console = Console()

@role_required("support")
def support_menu(user):
    console.print("[yellow]TODO : Menu support à implémenter[/yellow]")
    input("\nAppuyez sur Entrée pour continuer...")

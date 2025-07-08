from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def display_action_menu(actions, user=None):
    """
    Affiche un menu d’actions. Chaque action est un tuple :
    (choix, label, fonction_à_appeler)

    Si une fonction nécessite `user`, elle doit l'accepter en argument.
    """
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        valid_choices = [a[0] for a in actions]
        choice = Prompt.ask("\n[bold cyan]Votre choix[/bold cyan]", choices=valid_choices, default="0")

        if choice == "0":
            break

        for action in actions:
            if action[0] == choice:
                if len(action) > 2:
                    func = action[2]
                    if user is not None:
                        func(user)
                    else:
                        func()
                else:
                    console.print("[yellow]⚠️ Aucune action définie pour ce choix.[/yellow]")
                break

        input("\nAppuyez sur Entrée pour continuer...")

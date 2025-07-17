from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def safe_prompt_ask(prompt_text, choices, default="0"):
    """
    Version sécurisée de Prompt.ask pour éviter les erreurs en environnement de test (pas de stdin).
    """
    try:
        return Prompt.ask(prompt_text, choices=choices, default=default)
    except OSError:
        return default


def safe_input(prompt_text="\nAppuyez sur Entrée pour continuer..."):
    """
    Version sécurisée de input() pour éviter les erreurs en environnement de test.
    """
    try:
        input(prompt_text)
    except OSError:
        pass


def display_action_menu(actions, user=None):
    """
    Affiche un menu d’actions. Chaque action est un tuple :
    (choix, label, fonction_à_appeler)

    Si une fonction est décorée avec @role_required, elle n’a pas besoin d’argument.
    Si non décorée, elle accepte 'user' comme argument.
    """
    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Action")

        for choice, label, *_ in actions:
            table.add_row(choice, label)

        console.print(table)

        valid_choices = [a[0] for a in actions]
        choice = safe_prompt_ask("\n[bold cyan]Votre choix[/bold cyan]", choices=valid_choices, default="0")

        if choice == "0":
            break

        for action in actions:
            if action[0] == choice:
                func = action[2] if len(action) > 2 else None

                if func:
                    try:
                        # Test d'appel sans argument
                        func()
                    except TypeError as e:
                        if "positional argument" in str(e):
                            func(user)
                        else:
                            raise
                else:
                    console.print("[yellow]⚠️ Aucune action définie pour ce choix.[/yellow]")
                break

        safe_input()


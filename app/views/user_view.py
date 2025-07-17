from app.config import SessionLocal
from app.controllers.user_controller import create_user, update_user
from app.utils.auth import jwt_required, role_required
from app.models import Users
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

@jwt_required
@role_required("gestion")
def create_user_view(current_user, *args, **kwargs):  # Modification ici
    """Gère l'interface de création d'utilisateur"""
    session = SessionLocal()
    try:
        console.print("\n[bold]=== Création d'un nouveau collaborateur ===[/bold]")
        
        username = Prompt.ask("Nom d'utilisateur")
        first_name = Prompt.ask("Prénom")
        last_name = Prompt.ask("Nom")
        email = Prompt.ask("Email")
        password = Prompt.ask("Mot de passe", password=True)
        role_name = Prompt.ask(
            "Rôle (gestion/commercial/support)", 
            choices=["gestion", "commercial", "support"]
        )

        user, error = create_user(
            session,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role_name=role_name
        )

        if error:
            console.print(f"[red]{error}[/red]")
        else:
            console.print(f"[green]✅ Utilisateur {user.first_name} créé avec succès.[/green]")
    finally:
        session.close()

@jwt_required
@role_required("gestion")
def delete_user_view(current_user, *args, **kwargs):  # Modification ici
    """Gère l'interface de suppression d'utilisateur"""
    session = SessionLocal()
    try:
        users = session.query(Users).all()
        if not users:
            console.print("[red]Aucun utilisateur à supprimer.[/red]")
            return

        # Affichage tableau
        table = Table(title="Collaborateurs existants", header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Username")
        table.add_column("Email")
        table.add_column("Rôle")
        
        for user in users:
            table.add_row(str(user.id), user.username, user.email, user.role.name)
        
        console.print(table)

        # Sélection utilisateur
        user_id = Prompt.ask("\nID de l'utilisateur à supprimer")
        try:
            user_id = int(user_id)
        except ValueError:
            console.print("[red]L'ID doit être un nombre.[/red]")
            return

        user = session.query(Users).get(user_id)
        if not user:
            console.print(f"[red]Utilisateur avec ID {user_id} introuvable.[/red]")
            return

        if user.id == current_user.id:
            console.print("[red]Vous ne pouvez pas supprimer votre propre compte.[/red]")
            return

        # Confirmation
        if Confirm.ask(f"Confirmer la suppression de {user.username} ?", default=False):
            success, error = delete_user(session, user_id)
            if error:
                console.print(f"[red]{error}[/red]")
            else:
                console.print(f"[green]✅ Utilisateur supprimé avec succès.[/green]")
    finally:
        session.close()

@jwt_required
@role_required("gestion")
def update_user_view(current_user, *args, **kwargs):  # Modification ici
    """Gère l'interface de modification d'utilisateur"""
    session = SessionLocal()
    try:
        users = session.query(Users).all()
        if not users:
            console.print("[red]Aucun utilisateur trouvé.[/red]")
            return

        # Affichage tableau
        table = Table(title="Collaborateurs existants", header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Username")
        table.add_column("Email")
        table.add_column("Rôle")
        
        for user in users:
            table.add_row(str(user.id), user.username, user.email, user.role.name)
        
        console.print(table)

        # Sélection utilisateur
        user_id = Prompt.ask("\nID de l'utilisateur à modifier")
        try:
            user_id = int(user_id)
        except ValueError:
            console.print("[red]L'ID doit être un nombre.[/red]")
            return

        user = session.query(Users).get(user_id)
        if not user:
            console.print(f"[red]Utilisateur avec ID {user_id} introuvable.[/red]")
            return

        # Saisie modifications
        updates = {
            'username': Prompt.ask("Nouveau username", default=user.username),
            'first_name': Prompt.ask("Nouveau prénom", default=user.first_name),
            'last_name': Prompt.ask("Nouveau nom", default=user.last_name),
            'email': Prompt.ask("Nouvel email", default=user.email),
            'role_name': Prompt.ask(
                "Nouveau rôle", 
                choices=["gestion", "commercial", "support"],
                default=user.role.name
            )
        }

        if Confirm.ask("Changer le mot de passe ?", default=False):
            updates['password'] = Prompt.ask("Nouveau mot de passe", password=True)

        # Application modifications
        updated_user, error = update_user(session, user_id, **updates)
        if error:
            console.print(f"[red]{error}[/red]")
        else:
            console.print(f"[green]✅ Utilisateur mis à jour avec succès.[/green]")
    finally:
        session.close()

@jwt_required
def show_all_users_view(current_user, *args, **kwargs):  # Modification ici
    """Affiche la liste de tous les utilisateurs"""
    session = SessionLocal()
    try:
        users = session.query(Users).all()
        if not users:
            console.print("[red]Aucun utilisateur trouvé.[/red]")
            return

        table = Table(title="Liste des collaborateurs", header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Username")
        table.add_column("Prénom")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Rôle")
        
        for user in users:
            table.add_row(
                str(user.id),
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.role.name
            )
        
        console.print(table)
    finally:
        session.close()
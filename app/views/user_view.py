from app.config import SessionLocal
from app.controllers.user_controller import create_user, update_user
from app.utils.auth import jwt_required, role_required
from app.models import Users
from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm

@jwt_required
@role_required("gestion")
def create_user_view(current_user):
    if current_user.role.name != "gestion":
        print("⛔ Seul le département gestion peut créer un collaborateur.")
        return

    session = SessionLocal()

    print("\n=== Création d'un nouveau collaborateur ===")
    username = input("Nom d'utilisateur : ")
    first_name = input("Prénom : ")
    last_name = input("Nom : ")
    email = input("Email : ")
    password = input("Mot de passe : ")
    role_name = input("Rôle (gestion, commercial, support) : ")

    user, error = create_user(session, username, first_name, last_name, email, password, role_name)
    if error:
        print(error)
    else:
        print(f"✅ Utilisateur {user.first_name} créé avec succès.")

@jwt_required
@role_required("gestion")


def delete_user_view(current_user):
    session = SessionLocal()
    console = Console()

    users = session.query(Users).all()
    if not users:
        console.print("[red]Aucun utilisateur à supprimer.[/red]")
        return

    table = Table(title="🗑️ Collaborateurs existants", header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Username", style="green")
    table.add_column("Prénom", style="yellow")
    table.add_column("Nom", style="yellow")
    table.add_column("Email", style="blue")
    table.add_column("Rôle", style="magenta")

    for u in users:
        table.add_row(
            str(u.id),
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.role.name
        )

    console.print(table)

    print("\n=== Suppression d'un collaborateur ===")
    user_id_input = input("ID de l'utilisateur à supprimer : ").strip()

    try:
        user_id = int(user_id_input)
    except ValueError:
        console.print("[red]❌ L'ID doit être un nombre.[/red]")
        return

    user_to_delete = session.query(Users).filter_by(id=user_id).first()
    if not user_to_delete:
        console.print(f"[red]❌ Aucun utilisateur trouvé avec ID {user_id}.[/red]")
        return

    if user_to_delete.id == current_user.id:
        console.print("[red]❌ Vous ne pouvez pas vous supprimer vous-même.[/red]")
        return

    console.print(f"\n⚠️ Vous êtes sur le point de supprimer : [bold]{user_to_delete.username}[/bold] ({user_to_delete.email})")
    confirm = Confirm.ask("Confirmer la suppression ?", default=False)

    if confirm:
        session.delete(user_to_delete)
        session.commit()
        console.print(f"[green]✅ Utilisateur {user_to_delete.username} supprimé avec succès.[/green]")
    else:
        console.print("[yellow]❌ Suppression annulée.[/yellow]")


@jwt_required
@role_required("gestion")


def update_user_view(current_user):
    session = SessionLocal()
    console = Console()

    print("\n=== Liste des collaborateurs ===")
    users = session.query(Users).all()

    if not users:
        console.print("[red]Aucun utilisateur trouvé.[/red]")
        return

    table = Table(title="👥 Collaborateurs existants", header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Username", style="green")
    table.add_column("Prénom", style="yellow")
    table.add_column("Nom", style="yellow")
    table.add_column("Email", style="blue")
    table.add_column("Rôle", style="magenta")

    for u in users:
        table.add_row(
            str(u.id),
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.role.name
        )

    console.print(table)

    print("\n=== Modification d'un collaborateur ===")
    user_id = input("ID de l'utilisateur à modifier : ")

    try:
        user_id = int(user_id)
    except ValueError:
        console.print("[red]❌ L'ID doit être un nombre.[/red]")
        return

    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        console.print(f"[red]❌ Aucun utilisateur trouvé avec ID {user_id}.[/red]")
        return

    print(f"\nInfos actuelles pour {user.username} :")
    print(f"- Username : {user.username}")
    print(f"- Prénom   : {user.first_name}")
    print(f"- Nom      : {user.last_name}")
    print(f"- Email    : {user.email}")
    print(f"- Rôle     : {user.role.name}")

    updates = {}

    username = input(f"Nouveau username [{user.username}] : ").strip()
    if username:
        updates['username'] = username

    first_name = input(f"Nouveau prénom [{user.first_name}] : ").strip()
    if first_name:
        updates['first_name'] = first_name

    last_name = input(f"Nouveau nom [{user.last_name}] : ").strip()
    if last_name:
        updates['last_name'] = last_name

    email = input(f"Nouvel email [{user.email}] : ").strip()
    if email:
        updates['email'] = email

    password = input(f"Nouveau mot de passe [laisser vide pour ne pas changer] : ").strip()
    if password:
        updates['password'] = password

    role_name = input(f"Nouveau rôle [{user.role.name}] : ").strip()
    if role_name:
        updates['role_name'] = role_name

    if not updates:
        console.print("[red]❌ Aucun champ à modifier.[/red]")
        return

    updated_user, error = update_user(session, user_id, **updates)
    if error:
        console.print(f"[red]{error}[/red]")
    else:
        console.print(f"[green]✅ Collaborateur {updated_user.username} mis à jour avec succès.[/green]")


@jwt_required
def show_all_users_view(user):
    session = SessionLocal()
    users = session.query(Users).all()

    if not users:
        print("Aucun utilisateur trouvé.")
        return

    console = Console()

    table = Table(title=f"Liste des collaborateurs", header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Username", style="green")
    table.add_column("Prénom", style="yellow")
    table.add_column("Nom", style="yellow")
    table.add_column("Email", style="blue")
    table.add_column("Rôle", style="magenta")

    for u in users:
        table.add_row(
            str(u.id),
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.role.name
        )

    console.print(table)

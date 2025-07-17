from app.config import SessionLocal
from app.controllers.client_controller import list_all_clients, update_client, create_client
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_email, safe_input_int, safe_input_phone
from rich.console import Console
from rich.table import Table
from app.models import Clients
from rich.prompt import Prompt, Confirm

console = Console()

@jwt_required
@role_required("commercial", "gestion", "support")
def show_all_clients_view(current_user, *args, **kwargs):
    """Affiche la liste de tous les clients accessibles"""
    session = SessionLocal()
    try:
        clients = list_all_clients(session)

        if not clients:
            console.print("[red]Aucun client trouvé.[/red]")
            return

        table = Table(title=f"📋 Clients accessibles par {current_user.first_name}", 
                     header_style="bold magenta")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Prénom", style="yellow")
        table.add_column("Nom", style="yellow")
        table.add_column("Email", style="blue")
        table.add_column("Entreprise", style="green")

        for client in clients:
            table.add_row(
                str(client.id),
                client.first_name,
                client.last_name,
                client.email,
                client.company_name
            )

        console.print(table)
    finally:
        session.close()

@jwt_required
@role_required("commercial")
def create_client_view(current_user, *args, **kwargs):
    """Crée un nouveau client associé au commercial connecté"""
    session = SessionLocal()
    try:
        console.print("\n[bold]=== Création d'un nouveau client ===[/bold]")

        first_name = Prompt.ask("Prénom")
        last_name = Prompt.ask("Nom")
        email = safe_input_email("Email")
        phone = Prompt.ask("Téléphone")
        company_name = Prompt.ask("Nom de l'entreprise")

        client, error = create_client(
            session,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            commercial_id=current_user.id  # Assignation automatique
        )

        if error:
            console.print(f"[red]{error}[/red]")
        else:
            console.print(f"[green]✅ Client créé : {client.first_name} {client.last_name} (ID: {client.id})[/green]")
    finally:
        session.close()

@jwt_required
@role_required("commercial")
def update_client_view(current_user, *args, **kwargs):
    """Met à jour un client existant (uniquement ceux du commercial connecté)"""
    session = SessionLocal()
    try:
        console.print("\n[bold]=== Mise à jour d'un client ===[/bold]")

        # 🔒 Ne montrer que les clients du commercial connecté
        clients = session.query(Clients).filter_by(commercial_id=current_user.id).all()

        if not clients:
            console.print("[yellow]⚠️ Vous n'avez aucun client associé.[/yellow]")
            return

        # Affichage tableau
        table = Table(title="Vos clients", header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Nom complet")
        table.add_column("Email")
        table.add_column("Entreprise")
        
        for client in clients:
            table.add_row(
                str(client.id),
                f"{client.first_name} {client.last_name}",
                client.email,
                client.company_name
            )
        
        console.print(table)

        # Sélection client
        client_id = safe_input_int("\nID du client à modifier")
        if not client_id:
            return

        client = session.query(Clients).filter_by(id=client_id, commercial_id=current_user.id).first()
        if not client:
            console.print("[red]❌ Client introuvable ou non autorisé.[/red]")
            return

        # Affichage infos actuelles
        console.print(f"\n[bold]Informations actuelles du client ID {client.id}:[/bold]")
        info_table = Table(show_header=False)
        info_table.add_column("Champ", style="cyan")
        info_table.add_column("Valeur")
        
        info_table.add_row("Prénom", client.first_name)
        info_table.add_row("Nom", client.last_name)
        info_table.add_row("Email", client.email)
        info_table.add_row("Téléphone", client.phone or "Non renseigné")
        info_table.add_row("Société", client.company_name)
        
        console.print(info_table)

        # Saisie modifications
        updates = {
            "first_name": Prompt.ask("Nouveau prénom", default=client.first_name),
            "last_name": Prompt.ask("Nouveau nom", default=client.last_name),
            "company_name": Prompt.ask("Nouvelle société", default=client.company_name),
        }

        # Gestion spéciale email et téléphone
        new_email = Prompt.ask("Nouvel email", default=client.email)
        if new_email != client.email:
            updates["email"] = safe_input_email("Confirmer le nouvel email", default=new_email)

        new_phone = Prompt.ask("Nouveau téléphone", default=client.phone or "")
        if new_phone != (client.phone or ""):
            updates["phone"] = safe_input_phone("Confirmer le nouveau téléphone", default=new_phone)

        # Confirmation
        if Confirm.ask("\n[bold]Confirmer la modification ?[/bold]", default=False):
            updated_client, error = update_client(session, client_id, updates, current_user)
            if error:
                console.print(f"[red]{error}[/red]")
            else:
                console.print(f"[green]✅ Client mis à jour : {updated_client.first_name} {updated_client.last_name}[/green]")
        else:
            console.print("[yellow]Modification annulée[/yellow]")
    finally:
        session.close()
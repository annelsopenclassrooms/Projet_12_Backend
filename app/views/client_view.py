from app.config import SessionLocal
from app.controllers.client_controller import list_all_clients, update_client, create_client
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_email
from rich.console import Console
from rich.table import Table
from app.models import Clients

from app.utils.helpers import safe_input_int, safe_input_email, safe_input_phone

@jwt_required
@role_required("commercial", "gestion", "support")
def show_all_clients_view(user):
    session = SessionLocal()
    clients = list_all_clients(session)

    console = Console()

    if not clients:
        console.print("[red]Aucun client trouvé.[/red]")
        return

    table = Table(title=f"📋 Clients accessibles par {user.first_name}", header_style="bold magenta")
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

@jwt_required
@role_required("commercial")
def create_client_view(current_user):
    session = SessionLocal()

    print("\n=== Create a new client ===")

    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    email = safe_input_email("Email: ")
    phone = input("Phone: ").strip()
    company_name = input("Company name: ").strip()

    client, error = create_client(
        session,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_id=current_user.id  # Automatically assign current user
    )

    if error:
        print(error)
    else:
        print(f"✅ Client created: {client.first_name} {client.last_name} (ID: {client.id})")




@jwt_required
@role_required("commercial", "gestion")
def update_client_view(current_user):
    session = SessionLocal()

    print("\n=== Update a client ===")

    clients = session.query(Clients).all()
    print("\n📌 Clients list:")
    for client in clients:
        print(f"ID: {client.id} | {client.first_name} {client.last_name} | {client.email}")

    client_id = safe_input_int("\nEnter client ID to update: ")

    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        print("❌ Client not found.")
        return

    print(f"\nCurrent info for client ID {client.id}:")
    print(f"First name: {client.first_name}")
    print(f"Last name: {client.last_name}")
    print(f"Email: {client.email}")
    print(f"Phone: {client.phone}")
    print(f"Company name: {client.company_name}")

    first_name = input(f"New first name [{client.first_name}]: ").strip() or None
    last_name = input(f"New last name [{client.last_name}]: ").strip() or None

    email_input = input(f"New email [{client.email}]: ").strip()
    email = safe_input_email("Confirm new email: ") if email_input and email_input != client.email else None

    # Use phone helper
    phone_input = input(f"New phone [{client.phone}]: ").strip()
    phone = safe_input_phone("Confirm new phone: ") if phone_input and phone_input != client.phone else None

    company_name = input(f"New company name [{client.company_name}]: ").strip() or None

    updates = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
    }

    updated_client, error = update_client(session, client_id, updates, current_user)

    if error:
        print(error)
    else:
        print(f"✅ Client updated: {updated_client.first_name} {updated_client.last_name}")

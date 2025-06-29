from app.config import SessionLocal
from app.controllers.client_controller import list_all_clients, update_client, create_client
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_email

from app.models import Clients

from app.utils.helpers import safe_input_int, safe_input_email, safe_input_phone

@jwt_required
@role_required("commercial")
def show_all_clients(user):
    session = SessionLocal()
    clients = list_all_clients(session)

    if not clients:
        print("Aucun client trouvé.")
        return

    print(f"\n📋 Liste des clients accessibles par {user.first_name} :\n")
    for client in clients:
        print(f"- {client.first_name} {client.last_name} | {client.email} | {client.company_name}")

from app.config import SessionLocal
from app.controllers.client_controller import create_client
from app.utils.auth import jwt_required, role_required

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

from app.services.client_service import get_all_clients as service_get_all_clients
from app.models import Clients


def list_all_clients(session):
    clients = service_get_all_clients(session)
    return clients


def create_client(session, first_name, last_name, email, phone, company_name, commercial_id):
    # Check if email already exists
    existing_client = session.query(Clients).filter_by(email=email).first()
    if existing_client:
        return None, f"❌ A client with this email already exists."

    client = Clients(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_id=commercial_id
    )

    session.add(client)
    session.commit()

    return client, None


def update_client(session, client_id, updates, current_user):
    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        return None, f"❌ Client ID {client_id} not found."

    if current_user.role.name == "commercial" and client.commercial_id != current_user.id:
        return None, "⛔ You are not allowed to update this client."

    # If email is updated, check if it's unique
    new_email = updates.get("email")
    if new_email and new_email != client.email:
        existing_client = session.query(Clients).filter_by(email=new_email).first()
        if existing_client:
            return None, f"❌ This email is already used by another client."

    # Apply updates
    for field, value in updates.items():
        if value is not None:
            setattr(client, field, value)

    session.commit()
    return client, None

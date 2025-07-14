import sentry_sdk
from app.services.client_service import get_all_clients as service_get_all_clients
from app.models import Clients


def list_all_clients(session):
    clients = service_get_all_clients(session)
    return clients


def create_client(session, first_name, last_name, email, phone, company_name, commercial_id):
    try:
        existing_client = session.query(Clients).filter_by(email=email).first()
        if existing_client:
            return None, f"❌ Un client avec cet email existe déjà."

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

        # Sentry log: création
        sentry_sdk.capture_message(
            f"Client crée: {client.first_name} {client.last_name} | Email: {client.email} | ID Commercial: {commercial_id}",
            level="info"
        )

        return client, None

    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        return None, "❌ Erreur inattendue lors de la création du client."


def update_client(session, client_id, updates, current_user):
    try:
        client = session.query(Clients).filter_by(id=client_id).first()
        if not client:
            return None, f"❌ Client ID {client_id} introuvable."

        if current_user.role.name == "commercial" and client.commercial_id != current_user.id:
            return None, "⛔ Vous n’êtes pas autorisé·e à modifier ce client."

        new_email = updates.get("email")
        if new_email and new_email != client.email:
            existing_client = session.query(Clients).filter_by(email=new_email).first()
            if existing_client:
                return None, f"❌ Cet email est déjà utilisé par un autre client."

        for field, value in updates.items():
            if value is not None:
                setattr(client, field, value)

        session.commit()

        # Sentry log: modification
        sentry_sdk.capture_message(
            f"Client modifié : {client.first_name} {client.last_name} (ID : {client.id}) par l’utilisateur ID {current_user.id}",
            level="info"
        )

        return client, None

    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        return None, "❌ Erreur inattendue lors de la mise à jour du client."

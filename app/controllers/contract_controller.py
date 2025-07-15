from app.services.contract_service import get_all_contracts as service_get_all_contracts
from app.models import Contracts, Clients, Users
from datetime import datetime
from app.models import Contracts
import sentry_sdk


def list_all_contracts(session):
    contracts = service_get_all_contracts(session)
    return contracts


def create_contract(session, client_id, commercial_id, total_amount, amount_due, is_signed=False):
    # Check if the client exists
    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        return None, f"❌ Client ID {client_id} introuvable."

    # Check if the commercial exists and has the 'commercial' role
    commercial = session.query(Users).filter_by(id=commercial_id).first()
    if not commercial:
        return None, f"❌ Commercial ID {commercial_id} introuvable."

    if commercial.role.name != "commercial":
        return None, f"❌ L'utilisateur ID {commercial_id} n'est pas un commercial."

    contract = Contracts(
        client_id=client.id,
        commercial_id=commercial.id,
        total_amount=total_amount,
        amount_due=amount_due,
        is_signed=is_signed,
        date_created=datetime.utcnow()
    )

    session.add(contract)
    session.commit()

    # Log Sentry seulement si signé dès création
    if is_signed:
        sentry_sdk.capture_message(
            f"Contrat signé dès création : id={contract.id}, client_id={client.id}, commercial_id={commercial.id}, total_amount={total_amount}"
        )
    return contract, None


def update_contract(session, contract_id, updates, current_user):
    # Find the contract
    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        return None, f"❌ Contrat avec l’ID {contract_id} introuvable."

    # If user is commercial, verify they can edit this contract
    if current_user.role.name == "commercial" and contract.commercial_id != current_user.id:
        return None, "⛔ Vous n’êtes pas autorisé à modifier ce contrat."

    # Apply updates if values are provided
    for field, value in updates.items():
        if value is not None:
            setattr(contract, field, value)

    session.commit()

    # LOG signature Sentry si signé
    if updates.get("is_signed") is True:
        sentry_sdk.capture_message(
            f"Contrat signé : id={contract.id}, client_id={contract.client_id}, signé par user_id={current_user.id}"
        )


    return contract, None

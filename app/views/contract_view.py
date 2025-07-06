from app.config import SessionLocal
from app.controllers.contract_controller import list_all_contracts
from app.controllers.contract_controller import create_contract
from app.models import Clients, Users, Contracts
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_float, safe_input_yes_no
from app.controllers.contract_controller import update_contract


@jwt_required
def show_all_contracts_view(user):
    session = SessionLocal()
    contracts = list_all_contracts(session)

    if not contracts:
        print("Aucun contract trouvé.")
        return

    print(f"\n📋 Liste des contracts accessibles par {user.first_name} :\n")
    for contract in contracts:
        print(f"- {contract.id} {contract.client.company_name} {contract.is_signed} | {contract.amount_due} | {contract.date_created} | {contract.client.first_name}")


@jwt_required
@role_required("gestion", "commercial")
def create_contract_view(current_user):
    session = SessionLocal()

    print("\n=== Create a new contract ===")

    # List clients
    clients = session.query(Clients).all()
    print("\n📌 Existing clients:")
    for client in clients:
        print(f"ID: {client.id} | {client.first_name} {client.last_name} | Email: {client.email}")

    client_id = safe_input_int("Client ID: ")

    # List commercials
    commercials = session.query(Users).filter_by(role_id=2).all()
    print("\n📌 Existing commercials:")
    for c in commercials:
        print(f"ID: {c.id} | {c.first_name} {c.last_name} | {c.email}")

    commercial_id = safe_input_int("Commercial ID: ")

    total_amount = safe_input_float("Total contract amount: ")
    amount_due = safe_input_float("Remaining amount due: ")

    is_signed = safe_input_yes_no("Is the contract signed? (y/n) [n]: ", default=False)

    contract, error = create_contract(session, client_id, commercial_id, total_amount, amount_due, is_signed)

    if error:
        print(error)
    else:
        print(f"✅ Contract created with ID {contract.id} for client {contract.client.first_name} {contract.client.last_name}.")


@jwt_required
@role_required("gestion", "commercial")
def update_contract_view(current_user):
    session = SessionLocal()

    print("\n=== Update a contract ===")

    # Show all contracts with basic info
    contracts = session.query(Contracts).all()
    print("\n📌 Existing contracts:")
    for contract in contracts:
        client_name = contract.client.first_name + " " + contract.client.last_name
        print(f"ID: {contract.id} | Client: {client_name} | Total: {contract.total_amount} | Signed: {contract.is_signed}")

    contract_id = safe_input_int("\nEnter contract ID to update: ")

    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        print("❌ Contract not found.")
        return

    print(f"\nCurrent info for contract ID {contract.id}:")
    print(f"Client: {contract.client.first_name} {contract.client.last_name}")
    print(f"Commercial ID: {contract.commercial_id}")
    print(f"Total amount: {contract.total_amount}")
    print(f"Amount due: {contract.amount_due}")
    print(f"Signed: {contract.is_signed}")

    # Prompt for new values
    total_amount = safe_input_float(f"New total amount [{contract.total_amount}]: ") or None
    amount_due = safe_input_float(f"New amount due [{contract.amount_due}]: ") or None
    is_signed = safe_input_yes_no(f"Is signed (y/n) [currently {'Yes' if contract.is_signed else 'No'}]: ", default=contract.is_signed)

    updates = {
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }

    updated_contract, error = update_contract(session, contract_id, updates, current_user)

    if error:
        print(error)
    else:
        print(f"✅ Contract updated. Total: {updated_contract.total_amount}, Amount due: {updated_contract.amount_due}, Signed: {updated_contract.is_signed}")

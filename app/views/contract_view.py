from app.config import SessionLocal
from app.controllers.contract_controller import list_all_contracts
from app.utils.auth import jwt_required

@jwt_required
def show_all_contracts(user):
    session = SessionLocal()
    contracts = list_all_contracts(session)

    if not contracts:
        print("Aucun contract trouvé.")
        return

    print(f"\n📋 Liste des contracts accessibles par {user.first_name} :\n")
    for contract in contracts:
        print(f"- {contract.id} {contract.client.company_name} {contract.is_signed} | {contract.amount_due} | {contract.date_created} | {contract.client.first_name}")

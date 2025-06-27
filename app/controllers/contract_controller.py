from app.services.contract_service import get_all_contracts as service_get_all_contracts

def list_all_contracts(session):
    contracts = service_get_all_contracts(session)
    return contracts

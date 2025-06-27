from app.repositories.contract_repository import get_all_contracts as repo_get_all_contracts

def get_all_contracts(session):
    return repo_get_all_contracts(session)

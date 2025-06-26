from app.repositories.client_repository import get_all_clients as repo_get_all_clients

def get_all_clients(session):
    return repo_get_all_clients(session)

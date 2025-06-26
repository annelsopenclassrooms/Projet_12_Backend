from app.services.client_service import get_all_clients as service_get_all_clients

def list_all_clients(session):
    clients = service_get_all_clients(session)
    return clients

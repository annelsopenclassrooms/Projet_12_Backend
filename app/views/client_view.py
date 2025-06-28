from app.config import SessionLocal
from app.controllers.client_controller import list_all_clients
from app.utils.auth import jwt_required, role_required

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

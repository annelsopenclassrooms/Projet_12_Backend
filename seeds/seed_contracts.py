from app.config import SessionLocal
from app.models import Clients, Contracts, Users
from datetime import datetime
import random

def seed_contracts():
    session = SessionLocal()

    # Vérifier qu'il y a des clients
    clients = session.query(Clients).all()
    if not clients:
        print("❌ Aucun client trouvé. Veuillez d'abord lancer `seed_clients.py`.")
        return

    # Vérifier qu'il y a un commercial
    commercial = session.query(Users).filter(Users.role.has(name="commercial")).first()
    if not commercial:
        print("❌ Aucun commercial trouvé. Créez un commercial avant de créer des contrats.")
        return

    contracts_data = []

    for client in clients:
        total_amount = round(random.uniform(2000, 15000), 2)
        amount_due = round(random.uniform(0, total_amount), 2)
        is_signed = random.choice([True, False])

        contracts_data.append({
            "client_id": client.id,
            "commercial_id": commercial.id,
            "total_amount": total_amount,
            "amount_due": amount_due,
            "date_created": datetime.utcnow(),
            "is_signed": is_signed
        })

    for contract_data in contracts_data:
        contract = Contracts(**contract_data)
        session.add(contract)

    session.commit()
    print(f"✅ {len(contracts_data)} contrats insérés avec succès.")

if __name__ == "__main__":
    seed_contracts()

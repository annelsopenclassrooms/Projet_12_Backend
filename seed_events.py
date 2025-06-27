from app.config import SessionLocal
from app.models import Events, Contracts, Users
from datetime import datetime, timedelta
import random

def seed_events():
    session = SessionLocal()

    # Vérifier qu’il y a des contrats signés
    contracts = session.query(Contracts).filter_by(is_signed=True).all()
    if not contracts:
        print("❌ Aucun contrat signé trouvé. Veuillez vérifier vos contrats.")
        return

    # Vérifier qu’il y a un support disponible
    support = session.query(Users).filter(Users.role.has(name="support")).first()
    if not support:
        print("❌ Aucun support trouvé. Veuillez créer un utilisateur support.")
        return

    events_data = []
    for contract in contracts:
        start_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(hours=random.randint(4, 12))

        events_data.append({
            "name": f"Événement {contract.id}",
            "contract_id": contract.id,
            "client_id": contract.client_id,
            "support_contact_id": support.id,
            "date_start": start_date,
            "date_end": end_date,
            "location": f"{random.randint(1, 200)} Rue de Paris, France",
            "attendees": random.randint(10, 200),
            "notes": f"Organisation de l'événement pour le contrat {contract.id}."
        })

    for data in events_data:
        event = Events(**data)
        session.add(event)

    session.commit()
    print(f"✅ {len(events_data)} événements insérés avec succès.")

if __name__ == "__main__":
    seed_events()

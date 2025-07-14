from app.config import SessionLocal
from app.models import Clients, Users
from datetime import datetime

def seed_clients():
    session = SessionLocal()

    # Récupérer un commercial existant (premier utilisateur avec un rôle commercial)
    commercial = session.query(Users).filter(Users.role.has(name="commercial")).first()

    if not commercial:
        print("❌ Aucun commercial trouvé. Créez un utilisateur avec le rôle 'commercial' d'abord.")
        return

    clients_data = [
        {
            "first_name": "Élise",
            "last_name": "Moreau",
            "email": "elise.moreau@ateliersberthe.fr",
            "phone": "+33 6 12 34 56 78",
            "company_name": "Les Ateliers Berthe",
            "date_created": datetime(2022, 3, 15),
            "date_updated": datetime(2023, 4, 2)
        },
        {
            "first_name": "Jacques",
            "last_name": "Durand",
            "email": "jacques.durand@vinoble.fr",
            "phone": "+33 7 89 01 23 45",
            "company_name": "VinoBle",
            "date_created": datetime(2021, 11, 5),
            "date_updated": datetime(2023, 1, 18)
        },
        {
            "first_name": "Sophie",
            "last_name": "Blanchard",
            "email": "sophie@fromagesmollier.fr",
            "phone": "+33 6 77 55 44 33",
            "company_name": "Fromages Mollier",
            "date_created": datetime(2020, 6, 22),
            "date_updated": datetime(2023, 5, 10)
        },
        {
            "first_name": "Léon",
            "last_name": "Garnier",
            "email": "leon.garnier@evenementiel360.fr",
            "phone": "+33 6 65 23 78 90",
            "company_name": "Événementiel 360",
            "date_created": datetime(2022, 8, 30),
            "date_updated": datetime(2023, 4, 20)
        }
    ]

    for client_data in clients_data:
        client = Clients(**client_data, commercial=commercial)
        session.add(client)

    session.commit()
    print("✅ Clients insérés avec succès.")

if __name__ == "__main__":
    seed_clients()

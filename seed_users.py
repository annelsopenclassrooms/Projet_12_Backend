from app.config import SessionLocal
from app.models import Users, Roles
from app.utils.security import hash_password

# 🔑 Crée une session DB
session = SessionLocal()

# 🔑 Définir les rôles si pas encore présents
roles_data = ["gestion", "commercial", "support"]

for role_name in roles_data:
    role = session.query(Roles).filter_by(name=role_name).first()
    if not role:
        role = Roles(name=role_name)
        session.add(role)

session.commit()
print("✅ Rôles OK")

# 🔑 Liste des utilisateurs à créer
users_data = [
    {
        "username": "admin_gestion",
        "first_name": "Alice",
        "last_name": "Durand",
        "email": "alice.gestion@example.com",
        "password": "admin123",
        "role_name": "gestion"
    },
    {
        "username": "paul_commercial",
        "first_name": "Paul",
        "last_name": "Martin",
        "email": "paul.commercial@example.com",
        "password": "paulpass",
        "role_name": "commercial"
    },
    {
        "username": "sophie_support",
        "first_name": "Sophie",
        "last_name": "Lefevre",
        "email": "sophie.support@example.com",
        "password": "sophiepass",
        "role_name": "support"
    }
]

# 🔑 Créer les users sans doublons
for user_data in users_data:
    existing_user = session.query(Users).filter_by(email=user_data["email"]).first()
    if existing_user:
        print(f"⚠️ Utilisateur {user_data['email']} déjà présent, skip.")
        continue

    role = session.query(Roles).filter_by(name=user_data["role_name"]).first()
    if not role:
        print(f"❌ Rôle {user_data['role_name']} introuvable, skip.")
        continue

    user = Users(
        username=user_data["username"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
        role_id=role.id
    )
    session.add(user)
    print(f"✅ Utilisateur {user.username} ajouté.")

session.commit()
print("🎉 Seed terminé !")

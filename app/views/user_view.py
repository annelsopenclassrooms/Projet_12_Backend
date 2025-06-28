from app.config import SessionLocal
from app.controllers.user_controller import create_user
from app.utils.auth import jwt_required, role_required

@jwt_required
@role_required("gestion")
def create_user_view(current_user):
    if current_user.role.name != "gestion":
        print("⛔ Seul le département gestion peut créer un collaborateur.")
        return

    session = SessionLocal()

    print("\n=== Création d'un nouveau collaborateur ===")
    username = input("Nom d'utilisateur : ")
    first_name = input("Prénom : ")
    last_name = input("Nom : ")
    email = input("Email : ")
    password = input("Mot de passe : ")
    role_name = input("Rôle (gestion, commercial, support) : ")

    user, error = create_user(session, username, first_name, last_name, email, password, role_name)
    if error:
        print(error)
    else:
        print(f"✅ Utilisateur {user.first_name} créé avec succès.")

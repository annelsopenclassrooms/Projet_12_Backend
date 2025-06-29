from app.config import SessionLocal
from app.controllers.user_controller import create_user, update_user
from app.utils.auth import jwt_required, role_required
from app.models import Users


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


@jwt_required
@role_required("gestion")
def update_user_view(current_user):
    session = SessionLocal()

    print("\n=== Liste des collaborateurs ===")
    users = session.query(Users).all()
    for user in users:
        print(f"ID: {user.id} | Login: {user.username} | Rôle: {user.role.name}")

    print("\n=== Modification d'un collaborateur ===")
    user_id = input("ID de l'utilisateur à modifier : ")

    # Vérifie si l'ID est bien un nombre
    try:
        user_id = int(user_id)
    except ValueError:
        print("❌ L'ID doit être un nombre.")
        return

    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        print(f"❌ Aucun utilisateur trouvé avec ID {user_id}.")
        return

    print(f"Infos actuelles pour {user.username} :")
    print(f"- Username : {user.username}")
    print(f"- Prénom   : {user.first_name}")
    print(f"- Nom      : {user.last_name}")
    print(f"- Email    : {user.email}")
    print(f"- Rôle     : {user.role.name}")

    updates = {}

    username = input(f"Nouveau username [{user.username}] : ").strip()
    if username:
        updates['username'] = username

    first_name = input(f"Nouveau prénom [{user.first_name}] : ").strip()
    if first_name:
        updates['first_name'] = first_name

    last_name = input(f"Nouveau nom [{user.last_name}] : ").strip()
    if last_name:
        updates['last_name'] = last_name

    email = input(f"Nouvel email [{user.email}] : ").strip()
    if email:
        updates['email'] = email

    password = input(f"Nouveau mot de passe [laisser vide pour ne pas changer] : ").strip()
    if password:
        updates['password'] = password

    role_name = input(f"Nouveau rôle [{user.role.name}] : ").strip()
    if role_name:
        updates['role_name'] = role_name

    if not updates:
        print("❌ Aucun champ à modifier.")
        return

    updated_user, error = update_user(session, user_id, **updates)
    if error:
        print(error)
    else:
        print(f"✅ Collaborateur {updated_user.username} mis à jour avec succès.")

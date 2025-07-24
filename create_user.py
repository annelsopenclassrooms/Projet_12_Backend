"""Script interactif de création manuelle d'un utilisateur via SQLAlchemy."""

import getpass
from sqlalchemy.exc import IntegrityError
from app.config import SessionLocal, engine
from app.models import Base, Users, Roles
from passlib.context import CryptContext

# Contexte pour le hashage bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Retourne un mot de passe hashé (bcrypt)."""
    return pwd_context.hash(password)


def ensure_roles(session):
    """Crée les rôles de base si besoin."""
    for role_name in ("gestion", "commercial", "support"):
        if not session.query(Roles).filter_by(name=role_name).first():
            session.add(Roles(name=role_name))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("⚠️  Les rôles existaient déjà.")


def create_user(username: str, email: str, password: str, role_name: str = "gestion"):
    """Crée un utilisateur avec le rôle indiqué."""
    session = SessionLocal()
    try:
        # Vérifier que le rôle existe
        role = session.query(Roles).filter_by(name=role_name.lower()).first()
        if not role:
            print(f"Le rôle '{role_name}' n'existe pas. Vérifie la liste des rôles.")
            return

        # Vérifier que l'email ou le username n'existe pas déjà
        if session.query(Users).filter_by(email=email).first():
            print(f"❌ L'email {email} est déjà utilisé.")
            return

        if session.query(Users).filter_by(username=username).first():
            print(f"❌ Le username {username} est déjà utilisé.")
            return

        # Créer l'utilisateur
        user = Users(
            username=username,
            first_name=username.capitalize(),
            last_name="User",
            email=email,
            hashed_password=hash_password(password),
            role_id=role.id,
        )
        session.add(user)
        session.commit()
        print(f"✅ Utilisateur '{username}' créé avec succès (rôle: {role_name}).")

    except IntegrityError as e:
        session.rollback()
        print(f"Erreur d'intégrité : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    # 1. Créer les tables si elles n'existent pas
    print("🔧 Vérification de la base de données...")
    Base.metadata.create_all(bind=engine)

    # 2. Vérifier / créer les rôles
    session = SessionLocal()
    ensure_roles(session)
    session.close()

    # 3. Demander les infos utilisateur
    print("\n=== Création d'un nouvel utilisateur ===")
    username = input("Nom d'utilisateur : ").strip()
    email = input("Email : ").strip()
    password = getpass.getpass("Mot de passe : ")
    confirm_password = getpass.getpass("Confirmer le mot de passe : ")

    if password != confirm_password:
        print("❌ Les mots de passe ne correspondent pas. Abandon.")
    else:
        role_name = input("Rôle (gestion/commercial/support) [gestion] : ").strip() or "gestion"
        create_user(username, email, password, role_name)

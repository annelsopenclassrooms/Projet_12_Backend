# seed.py
"""Script de peuplement initial de la base : rôles et utilisateurs"""

from sqlalchemy.exc import IntegrityError
from app.config import SessionLocal, engine
from app.models import Base, Roles, Users
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Retourne un mot de passe hashé (bcrypt)."""
    return pwd_context.hash(password)


def seed_roles(session):
    """Crée les rôles de base si besoin."""
    for role_name in ("gestion", "commercial", "support"):
        if not session.query(Roles).filter_by(name=role_name).first():
            session.add(Roles(name=role_name))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Rôles déjà présents – ignoré.")


def seed_users(session):
    """Crée quelques comptes utilisateur de démonstration."""
    role_map = {r.name: r for r in session.query(Roles).all()}

    demo_users = [
        {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Manager",
            "email": "alice@epic.com",
            "password": "pass123",
            "role": "gestion",
        },
        {
            "username": "bob",
            "first_name": "Bob",
            "last_name": "Seller",
            "email": "bob@epic.com",
            "password": "pass123",
            "role": "commercial",
        },
        {
            "username": "charlie",
            "first_name": "Charlie",
            "last_name": "Helper",
            "email": "charlie@epic.com",
            "password": "pass123",
            "role": "support",
        },
    ]

    for data in demo_users:
        if not session.query(Users).filter_by(email=data["email"]).first():
            session.add(
                Users(
                    username=data["username"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    hashed_password=hash_password(data["password"]),
                    role_id=role_map[data["role"].lower()].id,
                )
            )
    try:
        session.commit()
        print("Utilisateurs insérés ou déjà présents.")
    except IntegrityError:
        session.rollback()
        print("Conflit lors de l'insertion des utilisateurs – rollback.")


def main():
    """Point d'entrée du script."""
    # S'assure que toutes les tables existent
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    seed_roles(session)
    seed_users(session)
    session.close()


if __name__ == "__main__":
    main()

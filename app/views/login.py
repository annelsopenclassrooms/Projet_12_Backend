import os
from getpass import getpass
from app.config import SessionLocal
from app.controllers.auth_controller import authenticate_user
from app.utils.jwt_handler import create_jwt_token

TOKEN_FILE = ".token"


def login():
    session = SessionLocal()
    print("== Connexion ==")
    login_input = input("Email ou nom d'utilisateur : ")
    password = getpass("Mot de passe : ")  # masque la saisie

    user, error = authenticate_user(session, login_input, password)

    if error:
        print("❌", error)
        return None

    token = create_jwt_token(user)

    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    print(f"✅ Bienvenue {user.first_name} ({user.role.name})")
    return user

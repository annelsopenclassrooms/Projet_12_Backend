import os
from app.config import SessionLocal
from app.models import Users
from app.utils.jwt_handler import decode_jwt_token
from functools import wraps

TOKEN_FILE = ".token"

def get_current_user():
    if not os.path.exists(TOKEN_FILE):
        print("🔒 Vous n'êtes pas connecté.")
        return None

    with open(TOKEN_FILE, "r") as f:
        token = f.read()

    payload, error = decode_jwt_token(token)

    if error:
        print(f"❌ Erreur d'authentification : {error}")
        print(token)
        return None

    session = SessionLocal()
    user = session.query(Users).get(payload["sub"])
    return user


def jwt_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            print("⛔ Accès refusé : vous devez être connecté.")
            return
        return func(user, *args, **kwargs)
    return wrapper

def role_required(*allowed_roles):
    """
    Décorateur pour vérifier que l'utilisateur a l'un des rôles autorisés.
    Usage : @role_required("gestion") ou @role_required("gestion", "admin")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.role.name not in allowed_roles:
                print(f"⛔ Accès refusé : rôle requis : {', '.join(allowed_roles)} | rôle actuel : {user.role.name}")
                return None
            return func(user, *args, **kwargs)
        return wrapper
    return decorator
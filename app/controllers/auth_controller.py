from sqlalchemy.orm import Session
from app.models import Users
from app.utils.security import verify_password
from sqlalchemy import or_

def authenticate_user(session: Session, username_or_email: str, password: str):
    """
    Authentifie un utilisateur par email ou nom d'utilisateur.
    Retourne (utilisateur, erreur) : erreur est None si authentification réussie.
    """
    user = session.query(Users).filter(
        or_(Users.email == username_or_email, Users.username == username_or_email)
    ).first()

    if not user or not verify_password(password, user.hashed_password):
        return None, "Identifiants invalides."

    return user, None

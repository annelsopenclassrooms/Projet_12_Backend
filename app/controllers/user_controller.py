from app.models import Users, Roles
from app.utils.security import hash_password
import sentry_sdk


def create_user(session, username, first_name, last_name, email, password, role_name):
    # check role existence
    role = session.query(Roles).filter_by(name=role_name).first()
    if not role:
        return None, f"❌ Rôle '{role_name}' introuvable."

    # check if user already exists
    if session.query(Users).filter_by(email=email).first():
        return None, f"❌ Un utilisateur existe déjà avec cet email : {email}"

    hashed_pw = hash_password(password)

    user = Users(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hashed_pw,
        role_id=role.id
    )
    session.add(user)
    session.commit()

    # LOG SENTRY
    sentry_sdk.capture_message(
        f"Utilisateur créé : id={user.id}, username={user.username}, email={user.email}, role={role_name}"
    )

    return user, None


def update_user(session, user_id, **updates):
    """
    Met à jour un collaborateur.
    `updates` peut contenir : username, first_name, last_name, email, password, role_name.
    """
    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        return None, f"❌ Utilisateur avec ID {user_id} introuvable."

    if 'username' in updates:
        user.username = updates['username']
    if 'first_name' in updates:
        user.first_name = updates['first_name']
    if 'last_name' in updates:
        user.last_name = updates['last_name']
    if 'email' in updates:
        # Vérifier doublon
        existing = session.query(Users).filter(Users.email == updates['email'], Users.id != user.id).first()
        if existing:
            return None, f"❌ Un autre utilisateur a déjà cet email : {updates['email']}"
        user.email = updates['email']
    if 'password' in updates:
        user.hashed_password = hash_password(updates['password'])
    if 'role_name' in updates:
        role = session.query(Roles).filter_by(name=updates['role_name']).first()
        if not role:
            return None, f"❌ Rôle '{updates['role_name']}' introuvable."
        user.role_id = role.id

    session.commit()

    # LOG SENTRY
    sentry_sdk.capture_message(
        f"Utilisateur modifié : id={user.id}, username={user.username}, email={user.email}, updates={list(updates.keys())}"
    )

    return user, None

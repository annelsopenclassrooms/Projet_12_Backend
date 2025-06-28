from app.models import Users, Roles
from app.utils.security import hash_password

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
    return user, None

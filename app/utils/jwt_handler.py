import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Lire les variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # valeur par défaut HS256
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", 600))


def create_jwt_token(user):
    payload = {
        "sub": str(user.id),  # erreur de decodage si pas de str
        "username": user.username,
        "role": user.role.name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expiré"
    except jwt.InvalidTokenError:
        return None, "Token invalide"

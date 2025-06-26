from datetime import datetime, timezone
import jwt
from app.utils.jwt_handler import create_jwt_token, decode_jwt_token

def main():
    # Exemple de classe User pour simuler un utilisateur
    class User:
        def __init__(self, id, username, role):
            self.id = id
            self.username = username
            self.role = Role(role)

    # Exemple de classe Role pour simuler un rôle
    class Role:
        def __init__(self, name):
            self.name = name

    # Créer un utilisateur fictif
    user = User(id=1, username="testuser", role="admin")

    # Générer un jeton JWT en utilisant la fonction existante
    token = create_jwt_token(user)
    print(f"Jeton généré: {token}")

    # Décoder le jeton JWT en utilisant la fonction existante
    payload, error = decode_jwt_token(token)

    if error:
        print(f"Erreur lors du décodage du jeton: {error}")
    else:
        print("Jeton décodé avec succès:")
        print(f"ID: {payload['sub']}")
        print(f"Nom d'utilisateur: {payload['username']}")
        print(f"Rôle: {payload['role']}")
        print(f"Date d'expiration: {datetime.fromtimestamp(payload['exp'], tz=timezone.utc)}")

if __name__ == "__main__":
    main()

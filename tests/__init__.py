import os
from cryptography.fernet import Fernet

# Définir FERNET_KEY si absent (avant tout import)
if "FERNET_KEY" not in os.environ:
    os.environ["FERNET_KEY"] = Fernet.generate_key().decode()
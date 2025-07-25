from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
import os

# Load encryption key from environment variable
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY is not set in environment variables.")

fernet = Fernet(FERNET_KEY)


class EncryptedString(TypeDecorator):
    """A SQLAlchemy column type for AES encryption/decryption using Fernet."""
    impl = String

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return fernet.decrypt(value.encode()).decode()

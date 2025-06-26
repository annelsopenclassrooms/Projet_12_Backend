from passlib.context import CryptContext

# Create a CryptContext instance configured to use the bcrypt hashing scheme.
# This context will handle the hashing and verification of passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password for storing.

    This function takes a plain text password and returns a hashed version of it.
    The CryptContext automatically generates a unique salt and hashes the password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password, which includes the salt and the hash.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against one provided by a user.

    This function checks if a plain text password matches the stored hashed password.
    It uses the salt stored in the hashed_password to hash the plain_password and compares the result.

    Args:
        plain_password (str): The plain text password provided by the user.
        hashed_password (str): The stored hashed password to verify against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

################################################################################
# File: ./all_files.py
################################################################################

epic_events/
│
├── app/
│   ├── models/              # Modèles ORM SQLAlchemy
│   │   └── models.py
│   │
│   ├── repositories/        # Requêtes vers la base de données (DAO / Repository)
│   │   ├── client_repository.py
│   │   └── ...
│   │
│   ├── services/            # Logique métier (use cases)
│   │   ├── client_service.py
│   │   └── ...
│   │
│   ├── controllers/         # Couche contrôleur : interface View → Service
│   │   ├── client_controller.py
│   │   └── ...
│   │
│   ├── views/               # Interface utilisateur (menus CLI)
│   │   ├── main_menu.py
│   │   └── client_view.py
│   │
│   ├── utils/               # Auth, logger, sentry, helpers
│   │   └── ...
│   │
│   └── config.py            # Connexion DB, constantes
│
├── tests/                   # Tests unitaires
│   └── test_clients.py
│
├── database.py              # Init DB
├── requirements.txt
└── main.py                  # Point d'entrée du programme


# models/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# models/role.py
from sqlalchemy import Column, Integer, String
from .base import Base

class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# models/user.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Roles')
    created_clients = relationship('Clients', back_populates='commercial')
    assigned_events = relationship('Events', back_populates='support_contact')


# models/client.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship('Users', back_populates='created_clients')

    contracts = relationship('Contracts', back_populates='client')
    events = relationship('Events', back_populates='client')


# models/contract.py
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Contracts(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    commercial_id = Column(Integer, ForeignKey('users.id'))

    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    client = relationship('Clients', back_populates='contracts')


# models/event.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    client = relationship('Clients', back_populates='events')
    support_contact = relationship('Users', back_populates='assigned_events')


# models/__init__.py
from .base import Base
from .role import Roles
from .user import Users
from .client import Clients
from .contract import Contracts
from .event import Events

# controllers/auth_controller.py


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


#utils/security.py

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

# utils/auth.py
import os
from app.config import SessionLocal
from app.models import Users
from app.utils.jwt_handler import decode_jwt_token

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

def role_gestion_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "gestion":
            print("⛔ Accès refusé : vous devez être gestion.")
            return
        return func(user, *args, **kwargs)
    return wrapper

def role_commercial_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "commercial":
            print("⛔ Accès refusé : vous devez être commercial.")
            return
        return func(user, *args, **kwargs)
    return wrapper

def role_support_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "support":
            print("⛔ Accès refusé : vous devez être support.")
            return
        return func(user, *args, **kwargs)
    return wrapper

#views/login.py

from app.config import SessionLocal
from app.controllers.auth_controller import authenticate_user

def login():
    session = SessionLocal()
    print("== Connexion ==")
    login_input = input("Email ou nom d'utilisateur : ")
    password = input("Mot de passe : ")

    user, error = authenticate_user(session, login_input, password)

    if error:
        print("❌", error)
        return None

    print(f"✅ Bienvenue {user.first_name} ({user.role.name})")
    return user

#app/config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de connexion SQLite
DATABASE_URL = "sqlite:///epic_events.db"

# Moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session locale (utilisable dans les services, contrôleurs, etc.)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# database.py

from app.config import engine
from app.models.base import Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")


################################################################################
# File: ./all_python_files_combined.py
################################################################################

################################################################################
# File: ./all_files.py
################################################################################

epic_events/
│
├── app/
│   ├── models/              # Modèles ORM SQLAlchemy
│   │   └── models.py
│   │
│   ├── repositories/        # Requêtes vers la base de données (DAO / Repository)
│   │   ├── client_repository.py
│   │   └── ...
│   │
│   ├── services/            # Logique métier (use cases)
│   │   ├── client_service.py
│   │   └── ...
│   │
│   ├── controllers/         # Couche contrôleur : interface View → Service
│   │   ├── client_controller.py
│   │   └── ...
│   │
│   ├── views/               # Interface utilisateur (menus CLI)
│   │   ├── main_menu.py
│   │   └── client_view.py
│   │
│   ├── utils/               # Auth, logger, sentry, helpers
│   │   └── ...
│   │
│   └── config.py            # Connexion DB, constantes
│
├── tests/                   # Tests unitaires
│   └── test_clients.py
│
├── database.py              # Init DB
├── requirements.txt
└── main.py                  # Point d'entrée du programme


# models/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# models/role.py
from sqlalchemy import Column, Integer, String
from .base import Base

class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# models/user.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Roles')
    created_clients = relationship('Clients', back_populates='commercial')
    assigned_events = relationship('Events', back_populates='support_contact')


# models/client.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship('Users', back_populates='created_clients')

    contracts = relationship('Contracts', back_populates='client')
    events = relationship('Events', back_populates='client')


# models/contract.py
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Contracts(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    commercial_id = Column(Integer, ForeignKey('users.id'))

    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    client = relationship('Clients', back_populates='contracts')


# models/event.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    client = relationship('Clients', back_populates='events')
    support_contact = relationship('Users', back_populates='assigned_events')


# models/__init__.py
from .base import Base
from .role import Roles
from .user import Users
from .client import Clients
from .contract import Contracts
from .event import Events

# controllers/auth_controller.py


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


#utils/security.py

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

# utils/auth.py
import os
from app.config import SessionLocal
from app.models import Users
from app.utils.jwt_handler import decode_jwt_token

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

def role_gestion_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "gestion":
            print("⛔ Accès refusé : vous devez être gestion.")
            return
        return func(user, *args, **kwargs)
    return wrapper

def role_commercial_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "commercial":
            print("⛔ Accès refusé : vous devez être commercial.")
            return
        return func(user, *args, **kwargs)
    return wrapper

def role_support_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        print (user.role.name)
        if not user.role.name == "support":
            print("⛔ Accès refusé : vous devez être support.")
            return
        return func(user, *args, **kwargs)
    return wrapper

#views/login.py

from app.config import SessionLocal
from app.controllers.auth_controller import authenticate_user

def login():
    session = SessionLocal()
    print("== Connexion ==")
    login_input = input("Email ou nom d'utilisateur : ")
    password = input("Mot de passe : ")

    user, error = authenticate_user(session, login_input, password)

    if error:
        print("❌", error)
        return None

    print(f"✅ Bienvenue {user.first_name} ({user.role.name})")
    return user

#app/config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de connexion SQLite
DATABASE_URL = "sqlite:///epic_events.db"

# Moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session locale (utilisable dans les services, contrôleurs, etc.)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# database.py

from app.config import engine
from app.models.base import Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")


################################################################################
# File: ./database.py
################################################################################

from app.config import engine
from app.models.base import Base


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")

################################################################################
# File: ./main.py
################################################################################

# main.py
from app.views.login import login
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def gestion_menu(user):
    console.print("\n📋 [bold cyan]Menu Gestion[/bold cyan]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Créer/Modifier un contrat")
    table.add_row("2", "Gérer les événements (attribution support)")
    table.add_row("3", "Créer/Modifier un utilisateur")
    console.print(table)
    Prompt.ask("Choisissez une option")

def commercial_menu(user):
    console.print("\n📋 [bold green]Menu Commercial[/bold green]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Créer un client")
    table.add_row("2", "Modifier un client")
    table.add_row("3", "Gérer les contrats clients")
    table.add_row("4", "Créer un événement")
    console.print(table)
    Prompt.ask("Choisissez une option")

def support_menu(user):
    console.print("\n📋 [bold magenta]Menu Support[/bold magenta]")
    table = Table(title="Options disponibles")
    table.add_column("Option", style="bold")
    table.add_column("Description")
    table.add_row("1", "Voir mes événements")
    table.add_row("2", "Mettre à jour un événement")
    console.print(table)
    Prompt.ask("Choisissez une option")

def main():
    user = login()
    if not user:
        return

    role = user.role.name.lower()
    if role == "gestion":
        gestion_menu(user)
    elif role == "commercial":
        commercial_menu(user)
    elif role == "support":
        support_menu(user)
    else:
        console.print("⚠️ [bold red]Rôle non reconnu.[/bold red]")

if __name__ == "__main__":
    main()


################################################################################
# File: ./recup.py
################################################################################

import os

def collect_py_files(root_dir, output_file):
    exclude_dirs = {'venv', 'env', '__pycache__'}

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for foldername, subfolders, filenames in os.walk(root_dir):
            # Exclure les dossiers indésirables
            subfolders[:] = [d for d in subfolders if d not in exclude_dirs]

            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(foldername, filename)
                    outfile.write('#' * 80 + '\n')
                    outfile.write(f'# File: {filepath}\n')
                    outfile.write('#' * 80 + '\n\n')
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            outfile.write('\n\n')
                    except Exception as e:
                        print(f"Could not read {filepath}: {e}")

if __name__ == '__main__':
    # Remplace ici par ton chemin de départ
    directory_to_scan = './'  # ou chemin absolu
    output_filename = 'all_python_files_combined.py'
    collect_py_files(directory_to_scan, output_filename)
    print(f'All .py files have been combined into {output_filename}')


################################################################################
# File: ./seed.py
################################################################################

# seed.py
"""Script de peuplement initial de la base : rôles et utilisateurs"""

from sqlalchemy.exc import IntegrityError
from app.config import SessionLocal, engine
from app.models import Base, Roles, Users
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Retourne un mot de passe hashé (bcrypt)."""
    return pwd_context.hash(password)


def seed_roles(session):
    """Crée les rôles de base si besoin."""
    for role_name in ("gestion", "commercial", "support"):
        if not session.query(Roles).filter_by(name=role_name).first():
            session.add(Roles(name=role_name))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Rôles déjà présents – ignoré.")


def seed_users(session):
    """Crée quelques comptes utilisateur de démonstration."""
    role_map = {r.name: r for r in session.query(Roles).all()}

    demo_users = [
        {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Manager",
            "email": "alice@epic.com",
            "password": "pass123",
            "role": "gestion",
        },
        {
            "username": "bob",
            "first_name": "Bob",
            "last_name": "Seller",
            "email": "bob@epic.com",
            "password": "pass123",
            "role": "commercial",
        },
        {
            "username": "charlie",
            "first_name": "Charlie",
            "last_name": "Helper",
            "email": "charlie@epic.com",
            "password": "pass123",
            "role": "support",
        },
    ]

    for data in demo_users:
        if not session.query(Users).filter_by(email=data["email"]).first():
            session.add(
                Users(
                    username=data["username"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    hashed_password=hash_password(data["password"]),
                    role_id=role_map[data["role"].lower()].id,
                )
            )
    try:
        session.commit()
        print("Utilisateurs insérés ou déjà présents.")
    except IntegrityError:
        session.rollback()
        print("Conflit lors de l'insertion des utilisateurs – rollback.")


def main():
    """Point d'entrée du script."""
    # S'assure que toutes les tables existent
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    seed_roles(session)
    seed_users(session)
    session.close()


if __name__ == "__main__":
    main()


################################################################################
# File: ./seed_client.py
################################################################################

from app.config import SessionLocal
from app.models import Clients, Users
from datetime import datetime

def seed_clients():
    session = SessionLocal()

    # Récupérer un commercial existant (premier utilisateur avec un rôle commercial)
    commercial = session.query(Users).filter(Users.role.has(name="commercial")).first()

    if not commercial:
        print("❌ Aucun commercial trouvé. Créez un utilisateur avec le rôle 'commercial' d'abord.")
        return

    clients_data = [
        {
            "first_name": "Élise",
            "last_name": "Moreau",
            "email": "elise.moreau@ateliersberthe.fr",
            "phone": "+33 6 12 34 56 78",
            "company_name": "Les Ateliers Berthe",
            "date_created": datetime(2022, 3, 15),
            "date_updated": datetime(2023, 4, 2)
        },
        {
            "first_name": "Jacques",
            "last_name": "Durand",
            "email": "jacques.durand@vinoble.fr",
            "phone": "+33 7 89 01 23 45",
            "company_name": "VinoBle",
            "date_created": datetime(2021, 11, 5),
            "date_updated": datetime(2023, 1, 18)
        },
        {
            "first_name": "Sophie",
            "last_name": "Blanchard",
            "email": "sophie@fromagesmollier.fr",
            "phone": "+33 6 77 55 44 33",
            "company_name": "Fromages Mollier",
            "date_created": datetime(2020, 6, 22),
            "date_updated": datetime(2023, 5, 10)
        },
        {
            "first_name": "Léon",
            "last_name": "Garnier",
            "email": "leon.garnier@evenementiel360.fr",
            "phone": "+33 6 65 23 78 90",
            "company_name": "Événementiel 360",
            "date_created": datetime(2022, 8, 30),
            "date_updated": datetime(2023, 4, 20)
        }
    ]

    for client_data in clients_data:
        client = Clients(**client_data, commercial=commercial)
        session.add(client)

    session.commit()
    print("✅ Clients insérés avec succès.")

if __name__ == "__main__":
    seed_clients()


################################################################################
# File: ./seed_contracts.py
################################################################################

from app.config import SessionLocal
from app.models import Clients, Contracts, Users
from datetime import datetime
import random

def seed_contracts():
    session = SessionLocal()

    # Vérifier qu'il y a des clients
    clients = session.query(Clients).all()
    if not clients:
        print("❌ Aucun client trouvé. Veuillez d'abord lancer `seed_clients.py`.")
        return

    # Vérifier qu'il y a un commercial
    commercial = session.query(Users).filter(Users.role.has(name="commercial")).first()
    if not commercial:
        print("❌ Aucun commercial trouvé. Créez un commercial avant de créer des contrats.")
        return

    contracts_data = []

    for client in clients:
        total_amount = round(random.uniform(2000, 15000), 2)
        amount_due = round(random.uniform(0, total_amount), 2)
        is_signed = random.choice([True, False])

        contracts_data.append({
            "client_id": client.id,
            "commercial_id": commercial.id,
            "total_amount": total_amount,
            "amount_due": amount_due,
            "date_created": datetime.utcnow(),
            "is_signed": is_signed
        })

    for contract_data in contracts_data:
        contract = Contracts(**contract_data)
        session.add(contract)

    session.commit()
    print(f"✅ {len(contracts_data)} contrats insérés avec succès.")

if __name__ == "__main__":
    seed_contracts()


################################################################################
# File: ./seed_events.py
################################################################################

from app.config import SessionLocal
from app.models import Events, Contracts, Users
from datetime import datetime, timedelta
import random

def seed_events():
    session = SessionLocal()

    # Vérifier qu’il y a des contrats signés
    contracts = session.query(Contracts).filter_by(is_signed=True).all()
    if not contracts:
        print("❌ Aucun contrat signé trouvé. Veuillez vérifier vos contrats.")
        return

    # Vérifier qu’il y a un support disponible
    support = session.query(Users).filter(Users.role.has(name="support")).first()
    if not support:
        print("❌ Aucun support trouvé. Veuillez créer un utilisateur support.")
        return

    events_data = []
    for contract in contracts:
        start_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(hours=random.randint(4, 12))

        events_data.append({
            "name": f"Événement {contract.id}",
            "contract_id": contract.id,
            "client_id": contract.client_id,
            "support_contact_id": support.id,
            "date_start": start_date,
            "date_end": end_date,
            "location": f"{random.randint(1, 200)} Rue de Paris, France",
            "attendees": random.randint(10, 200),
            "notes": f"Organisation de l'événement pour le contrat {contract.id}."
        })

    for data in events_data:
        event = Events(**data)
        session.add(event)

    session.commit()
    print(f"✅ {len(events_data)} événements insérés avec succès.")

if __name__ == "__main__":
    seed_events()


################################################################################
# File: ./seed_users.py
################################################################################

from app.config import SessionLocal
from app.models import Users, Roles
from app.utils.security import hash_password

# 🔑 Crée une session DB
session = SessionLocal()

# 🔑 Définir les rôles si pas encore présents
roles_data = ["gestion", "commercial", "support"]

for role_name in roles_data:
    role = session.query(Roles).filter_by(name=role_name).first()
    if not role:
        role = Roles(name=role_name)
        session.add(role)

session.commit()
print("✅ Rôles OK")

# 🔑 Liste des utilisateurs à créer
users_data = [
    {
        "username": "admin_gestion",
        "first_name": "Alice",
        "last_name": "Durand",
        "email": "alice.gestion@example.com",
        "password": "admin123",
        "role_name": "gestion"
    },
    {
        "username": "paul_commercial",
        "first_name": "Paul",
        "last_name": "Martin",
        "email": "paul.commercial@example.com",
        "password": "paulpass",
        "role_name": "commercial"
    },
    {
        "username": "sophie_support",
        "first_name": "Sophie",
        "last_name": "Lefevre",
        "email": "sophie.support@example.com",
        "password": "sophiepass",
        "role_name": "support"
    }
]

# 🔑 Créer les users sans doublons
for user_data in users_data:
    existing_user = session.query(Users).filter_by(email=user_data["email"]).first()
    if existing_user:
        print(f"⚠️ Utilisateur {user_data['email']} déjà présent, skip.")
        continue

    role = session.query(Roles).filter_by(name=user_data["role_name"]).first()
    if not role:
        print(f"❌ Rôle {user_data['role_name']} introuvable, skip.")
        continue

    user = Users(
        username=user_data["username"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
        role_id=role.id
    )
    session.add(user)
    print(f"✅ Utilisateur {user.username} ajouté.")

session.commit()
print("🎉 Seed terminé !")


################################################################################
# File: ./test_create_contract.py
################################################################################

from app.views.contract_view import create_contract_view
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    

    create_contract_view()

if __name__ == "__main__":
    main()

################################################################################
# File: ./test_create_event.py
################################################################################

from app.views.contract_view import create_contract_view
from app.views.event_view import create_event_view
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    

    create_event_view()

if __name__ == "__main__":
    main()

################################################################################
# File: ./test_modify_user.py
################################################################################

from app.views.user_view import create_user_view, update_user_view
from app.config import SessionLocal
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    
    
    update_user_view()


if __name__ == "__main__":
    main()

################################################################################
# File: ./app/config.py
################################################################################

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de connexion SQLite
DATABASE_URL = "sqlite:///epic_events.db"

# Moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session locale (utilisable dans les services, contrôleurs, etc.)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


################################################################################
# File: ./app/__init__.py
################################################################################



################################################################################
# File: ./app/controllers/auth_controller.py
################################################################################

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


################################################################################
# File: ./app/controllers/client_controller.py
################################################################################

from app.services.client_service import get_all_clients as service_get_all_clients
from app.models import Clients


def list_all_clients(session):
    clients = service_get_all_clients(session)
    return clients


def create_client(session, first_name, last_name, email, phone, company_name, commercial_id):
    # Check if email already exists
    existing_client = session.query(Clients).filter_by(email=email).first()
    if existing_client:
        return None, f"❌ A client with this email already exists."

    client = Clients(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_id=commercial_id
    )

    session.add(client)
    session.commit()

    return client, None


def update_client(session, client_id, updates, current_user):
    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        return None, f"❌ Client ID {client_id} not found."

    if current_user.role.name == "commercial" and client.commercial_id != current_user.id:
        return None, "⛔ You are not allowed to update this client."

    # If email is updated, check if it's unique
    new_email = updates.get("email")
    if new_email and new_email != client.email:
        existing_client = session.query(Clients).filter_by(email=new_email).first()
        if existing_client:
            return None, f"❌ This email is already used by another client."

    # Apply updates
    for field, value in updates.items():
        if value is not None:
            setattr(client, field, value)

    session.commit()
    return client, None


################################################################################
# File: ./app/controllers/contract_controller.py
################################################################################

from app.services.contract_service import get_all_contracts as service_get_all_contracts
from app.models import Contracts, Clients, Users
from datetime import datetime
from app.models import Contracts


def list_all_contracts(session):
    contracts = service_get_all_contracts(session)
    return contracts


def create_contract(session, client_id, commercial_id, total_amount, amount_due, is_signed=False):
    # Check if the client exists
    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        return None, f"❌ Client ID {client_id} introuvable."

    # Check if the commercial exists and has the 'commercial' role
    commercial = session.query(Users).filter_by(id=commercial_id).first()
    if not commercial:
        return None, f"❌ Commercial ID {commercial_id} introuvable."

    if commercial.role.name != "commercial":
        return None, f"❌ L'utilisateur ID {commercial_id} n'est pas un commercial."

    contract = Contracts(
        client_id=client.id,
        commercial_id=commercial.id,
        total_amount=total_amount,
        amount_due=amount_due,
        is_signed=is_signed,
        date_created=datetime.utcnow()
    )

    session.add(contract)
    session.commit()

    return contract, None


def update_contract(session, contract_id, updates, current_user):
    # Find the contract
    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        return None, f"❌ Contract ID {contract_id} not found."

    # If user is commercial, verify they can edit this contract
    if current_user.role.name == "commercial" and contract.commercial_id != current_user.id:
        return None, "⛔ You are not allowed to update this contract."

    # Apply updates if values are provided
    for field, value in updates.items():
        if value is not None:
            setattr(contract, field, value)

    session.commit()
    return contract, None


################################################################################
# File: ./app/controllers/event_controller.py
################################################################################

from app.services.event_service import get_all_events as service_get_all_events
from app.models import Events, Clients, Contracts, Users


def list_all_events(session):
    events = service_get_all_events(session)
    return events


def create_event(session, name, contract_id, client_id, support_contact_id, date_start, date_end, location, attendees, notes):
    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        return None, f"❌ Client ID {client_id} not found."

    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        return None, f"❌ Contract ID {contract_id} not found."

    support_contact = session.query(Users).filter_by(id=support_contact_id).first()
    if not support_contact or support_contact.role.name != "support":
        return None, f"❌ Support contact ID {support_contact_id} invalid."

    event = Events(
        name=name,
        contract_id=contract_id,
        client_id=client_id,
        support_contact_id=support_contact_id,
        date_start=date_start,
        date_end=date_end,
        location=location,
        attendees=attendees,
        notes=notes
    )

    session.add(event)
    session.commit()

    return event, None


def update_event(session, event_id, updates, current_user):
    # Find the event
    event = session.query(Events).filter_by(id=event_id).first()
    if not event:
        return None, f"❌ Event ID {event_id} not found."

    # If user is support, ensure they are assigned to this event
    if current_user.role.name == "support" and event.support_contact_id != current_user.id:
        return None, "⛔ You are not allowed to update this event."

    # Apply updates if not None
    for field, value in updates.items():
        if value is not None:
            setattr(event, field, value)

    session.commit()
    return event, None



################################################################################
# File: ./app/controllers/user_controller.py
################################################################################

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
    return user, None


################################################################################
# File: ./app/models/base.py
################################################################################

from sqlalchemy.orm import declarative_base

Base = declarative_base()



################################################################################
# File: ./app/models/client.py
################################################################################

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship('Users', back_populates='created_clients')

    contracts = relationship('Contracts', back_populates='client')
    events = relationship('Events', back_populates='client')

################################################################################
# File: ./app/models/contract.py
################################################################################

from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Contracts(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    commercial_id = Column(Integer, ForeignKey('users.id'))

    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    client = relationship('Clients', back_populates='contracts')



################################################################################
# File: ./app/models/event.py
################################################################################

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)

    client = relationship('Clients', back_populates='events')
    support_contact = relationship('Users', back_populates='assigned_events')

################################################################################
# File: ./app/models/role.py
################################################################################

# models/role.py
from sqlalchemy import Column, Integer, String
from .base import Base

class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

################################################################################
# File: ./app/models/user.py
################################################################################

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Roles')
    created_clients = relationship('Clients', back_populates='commercial')
    assigned_events = relationship('Events', back_populates='support_contact')

################################################################################
# File: ./app/models/__init__.py
################################################################################

from .base import Base
from .role import Roles
from .user import Users
from .client import Clients
from .contract import Contracts
from .event import Events

################################################################################
# File: ./app/repositories/client_repository.py
################################################################################

from sqlalchemy.orm import Session
from app.models import Clients

def get_all_clients(session: Session):
    return session.query(Clients).order_by(Clients.last_name).all()


################################################################################
# File: ./app/repositories/contract_repository.py
################################################################################

from sqlalchemy.orm import Session, joinedload
from app.models import Contracts

def get_all_contracts(session: Session):
    """
    Récupère tous les contrats, avec leur client préchargé.
    """
    return (
        session.query(Contracts)
        .options(joinedload(Contracts.client))
        .order_by(Contracts.date_created.desc())
        .all()
    )

################################################################################
# File: ./app/repositories/event_repository.py
################################################################################

from sqlalchemy.orm import Session, joinedload
from app.models import Events

def get_all_events(session: Session):
    """
    Récupère tous les contrats, avec leur client préchargé.
    """
    return (
        session.query(Events)
        .options(joinedload(Events.client))
        .order_by(Events.date_start.desc())
        .all()
    )

################################################################################
# File: ./app/services/client_service.py
################################################################################

from app.repositories.client_repository import get_all_clients as repo_get_all_clients

def get_all_clients(session):
    return repo_get_all_clients(session)


################################################################################
# File: ./app/services/contract_service.py
################################################################################

from app.repositories.contract_repository import get_all_contracts as repo_get_all_contracts

def get_all_contracts(session):
    return repo_get_all_contracts(session)


################################################################################
# File: ./app/services/event_service.py
################################################################################

from app.repositories.event_repository import get_all_events as repo_get_all_events

def get_all_events(session):
    return repo_get_all_events(session)


################################################################################
# File: ./app/utils/auth.py
################################################################################

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

################################################################################
# File: ./app/utils/helpers.py
################################################################################

from datetime import datetime
import re


def safe_input_int(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("❌ Please enter a valid number.")


def safe_input_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("❌ Please enter a valid number.")


def safe_input_yes_no(prompt, default=False):
    while True:
        value = input(prompt).strip().lower()
        if not value:
            return default
        if value in ["y", "yes", "o", "oui"]:
            return True
        elif value in ["n", "no", "non"]:
            return False
        else:
            print("❌ Please answer y/n.")


def safe_input_date(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Please enter a valid date (YYYY-MM-DD).")


def safe_input_choice(prompt, choices):
    choices_str = [str(choice) for choice in choices]
    while True:
        value = input(f"{prompt} ({'/'.join(choices_str)}): ").strip()
        if value in choices_str:
            for c in choices:
                if str(c) == value:
                    return c
        print(f"❌ Please enter a valid choice: {', '.join(choices_str)}")


def safe_input_email(prompt):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    while True:
        value = input(prompt).strip()
        if re.match(pattern, value):
            return value
        print("❌ Please enter a valid email.")


def safe_input_phone(prompt):
    """
    Prompt for a valid phone number (simple check).
    Accepts digits, +, spaces, -.
    """
    pattern = r"^[\d +()-]{5,20}$"
    while True:
        value = input(prompt).strip()
        if re.match(pattern, value):
            return value
        print("❌ Please enter a valid phone number.")


################################################################################
# File: ./app/utils/jwt_handler.py
################################################################################

import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "SUPER_SECRET_KEY"  # à mettre dans .env
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 1000  # durée de validité

def create_jwt_token(user):
    payload = {
        "sub": str(user.id),#erreur de decodage si pas de str
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


################################################################################
# File: ./app/utils/security.py
################################################################################

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


################################################################################
# File: ./app/views/client_view.py
################################################################################

from app.config import SessionLocal
from app.controllers.client_controller import list_all_clients, update_client, create_client
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_email

from app.models import Clients

from app.utils.helpers import safe_input_int, safe_input_email, safe_input_phone

@jwt_required
@role_required("commercial")
def show_all_clients(user):
    session = SessionLocal()
    clients = list_all_clients(session)

    if not clients:
        print("Aucun client trouvé.")
        return

    print(f"\n📋 Liste des clients accessibles par {user.first_name} :\n")
    for client in clients:
        print(f"- {client.first_name} {client.last_name} | {client.email} | {client.company_name}")

from app.config import SessionLocal
from app.controllers.client_controller import create_client
from app.utils.auth import jwt_required, role_required

@jwt_required
@role_required("commercial")
def create_client_view(current_user):
    session = SessionLocal()

    print("\n=== Create a new client ===")

    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    email = safe_input_email("Email: ")
    phone = input("Phone: ").strip()
    company_name = input("Company name: ").strip()

    client, error = create_client(
        session,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_id=current_user.id  # Automatically assign current user
    )

    if error:
        print(error)
    else:
        print(f"✅ Client created: {client.first_name} {client.last_name} (ID: {client.id})")




@jwt_required
@role_required("commercial", "gestion")
def update_client_view(current_user):
    session = SessionLocal()

    print("\n=== Update a client ===")

    clients = session.query(Clients).all()
    print("\n📌 Clients list:")
    for client in clients:
        print(f"ID: {client.id} | {client.first_name} {client.last_name} | {client.email}")

    client_id = safe_input_int("\nEnter client ID to update: ")

    client = session.query(Clients).filter_by(id=client_id).first()
    if not client:
        print("❌ Client not found.")
        return

    print(f"\nCurrent info for client ID {client.id}:")
    print(f"First name: {client.first_name}")
    print(f"Last name: {client.last_name}")
    print(f"Email: {client.email}")
    print(f"Phone: {client.phone}")
    print(f"Company name: {client.company_name}")

    first_name = input(f"New first name [{client.first_name}]: ").strip() or None
    last_name = input(f"New last name [{client.last_name}]: ").strip() or None

    email_input = input(f"New email [{client.email}]: ").strip()
    email = safe_input_email("Confirm new email: ") if email_input and email_input != client.email else None

    # Use phone helper
    phone_input = input(f"New phone [{client.phone}]: ").strip()
    phone = safe_input_phone("Confirm new phone: ") if phone_input and phone_input != client.phone else None

    company_name = input(f"New company name [{client.company_name}]: ").strip() or None

    updates = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
    }

    updated_client, error = update_client(session, client_id, updates, current_user)

    if error:
        print(error)
    else:
        print(f"✅ Client updated: {updated_client.first_name} {updated_client.last_name}")


################################################################################
# File: ./app/views/contract_view.py
################################################################################

from app.config import SessionLocal
from app.controllers.contract_controller import list_all_contracts
from app.controllers.contract_controller import create_contract
from app.models import Clients, Users, Contracts
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_float, safe_input_yes_no
from app.controllers.contract_controller import update_contract


@jwt_required
def show_all_contracts(user):
    session = SessionLocal()
    contracts = list_all_contracts(session)

    if not contracts:
        print("Aucun contract trouvé.")
        return

    print(f"\n📋 Liste des contracts accessibles par {user.first_name} :\n")
    for contract in contracts:
        print(f"- {contract.id} {contract.client.company_name} {contract.is_signed} | {contract.amount_due} | {contract.date_created} | {contract.client.first_name}")


@jwt_required
@role_required("gestion", "commercial")
def create_contract_view(current_user):
    session = SessionLocal()

    print("\n=== Create a new contract ===")

    # List clients
    clients = session.query(Clients).all()
    print("\n📌 Existing clients:")
    for client in clients:
        print(f"ID: {client.id} | {client.first_name} {client.last_name} | Email: {client.email}")

    client_id = safe_input_int("Client ID: ")

    # List commercials
    commercials = session.query(Users).filter_by(role_id=2).all()
    print("\n📌 Existing commercials:")
    for c in commercials:
        print(f"ID: {c.id} | {c.first_name} {c.last_name} | {c.email}")

    commercial_id = safe_input_int("Commercial ID: ")

    total_amount = safe_input_float("Total contract amount: ")
    amount_due = safe_input_float("Remaining amount due: ")

    is_signed = safe_input_yes_no("Is the contract signed? (y/n) [n]: ", default=False)

    contract, error = create_contract(session, client_id, commercial_id, total_amount, amount_due, is_signed)

    if error:
        print(error)
    else:
        print(f"✅ Contract created with ID {contract.id} for client {contract.client.first_name} {contract.client.last_name}.")


@jwt_required
@role_required("gestion", "commercial")
def update_contract_view(current_user):
    session = SessionLocal()

    print("\n=== Update a contract ===")

    # Show all contracts with basic info
    contracts = session.query(Contracts).all()
    print("\n📌 Existing contracts:")
    for contract in contracts:
        client_name = contract.client.first_name + " " + contract.client.last_name
        print(f"ID: {contract.id} | Client: {client_name} | Total: {contract.total_amount} | Signed: {contract.is_signed}")

    contract_id = safe_input_int("\nEnter contract ID to update: ")

    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        print("❌ Contract not found.")
        return

    print(f"\nCurrent info for contract ID {contract.id}:")
    print(f"Client: {contract.client.first_name} {contract.client.last_name}")
    print(f"Commercial ID: {contract.commercial_id}")
    print(f"Total amount: {contract.total_amount}")
    print(f"Amount due: {contract.amount_due}")
    print(f"Signed: {contract.is_signed}")

    # Prompt for new values
    total_amount = safe_input_float(f"New total amount [{contract.total_amount}]: ") or None
    amount_due = safe_input_float(f"New amount due [{contract.amount_due}]: ") or None
    is_signed = safe_input_yes_no(f"Is signed (y/n) [currently {'Yes' if contract.is_signed else 'No'}]: ", default=contract.is_signed)

    updates = {
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }

    updated_contract, error = update_contract(session, contract_id, updates, current_user)

    if error:
        print(error)
    else:
        print(f"✅ Contract updated. Total: {updated_contract.total_amount}, Amount due: {updated_contract.amount_due}, Signed: {updated_contract.is_signed}")


################################################################################
# File: ./app/views/event_view.py
################################################################################

from app.config import SessionLocal
from app.controllers.event_controller import list_all_events
from app.models import Clients, Contracts, Users, Events
from app.controllers.event_controller import create_event
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_date
from app.controllers.event_controller import update_event


@jwt_required
def show_all_events(user):
    session = SessionLocal()
    events = list_all_events(session)

    if not events:
        print("Aucun event trouvé.")
        return

    print(f"\n📋 Liste des events accessibles par {user.first_name} :\n")
    for event in events:
        print(f"- {event.name} {event.client.company_name} {event.date_start} | {event.date_end} | {event.location} | {event.attendees}")


@jwt_required
@role_required("gestion", "commercial")
def create_event_view(current_user):
    session = SessionLocal()

    print("\n=== Create a new event ===")

    # Show clients for reference
    clients = session.query(Clients).all()
    print("\n📌 Existing clients:")
    for client in clients:
        print(f"ID: {client.id} | {client.first_name} {client.last_name} | {client.email}")

    client_id = safe_input_int("Client ID: ")

    # Show contracts for reference
    contracts = session.query(Contracts).filter_by(client_id=client_id).all()
    if not contracts:
        print(f"❌ No contracts found for client ID {client_id}.")
        return

    print("\n📌 Existing contracts for this client:")
    for contract in contracts:
        print(f"ID: {contract.id} | Total: {contract.total_amount} | Signed: {'Yes' if contract.is_signed else 'No'}")

    contract_id = safe_input_int("Contract ID: ")

    # Show support users
    support_users = session.query(Users).filter(Users.role.has(name="support")).all()
    print("\n📌 Available support contacts:")
    for user in support_users:
        print(f"ID: {user.id} | {user.first_name} {user.last_name} | {user.email}")

    support_contact_id = safe_input_int("Support contact ID: ")

    name = input("Event name: ").strip()

    # Here we use the date helper!
    date_start = safe_input_date("Event start date (YYYY-MM-DD): ")
    date_end = safe_input_date("Event end date (YYYY-MM-DD): ")

    location = input("Event location: ").strip()
    attendees = safe_input_int("Number of attendees: ")

    notes = input("Notes: ").strip()

    # Call your controller (make sure you have it)
    event, error = create_event(
        session,
        name=name,
        contract_id=contract_id,
        client_id=client_id,
        support_contact_id=support_contact_id,
        date_start=date_start,
        date_end=date_end,
        location=location,
        attendees=attendees,
        notes=notes
    )

    if error:
        print(error)
    else:
        print(f"✅ Event created: {event.name} (ID: {event.id})")


@jwt_required
@role_required("gestion", "support")
def update_event_view(current_user):
    session = SessionLocal()

    print("\n=== Update an event ===")

    # Show all events
    events = session.query(Events).all()
    print("\n📌 Existing events:")
    for event in events:
        print(f"ID: {event.id} | Name: {event.name} | Client: {event.client.first_name} {event.client.last_name} | Support: {event.support_contact.first_name if event.support_contact else 'None'}")

    event_id = safe_input_int("\nEnter event ID to update: ")

    event = session.query(Events).filter_by(id=event_id).first()
    if not event:
        print("❌ Event not found.")
        return

    print(f"\nCurrent info for event ID {event.id}:")
    print(f"Name: {event.name}")
    print(f"Start: {event.date_start}")
    print(f"End: {event.date_end}")
    print(f"Location: {event.location}")
    print(f"Attendees: {event.attendees}")
    print(f"Notes: {event.notes}")
    print(f"Support contact: {event.support_contact_id}")

    # Prompt new values (optional)
    name = input(f"New name [{event.name}]: ").strip() or None
    date_start = safe_input_date(f"New start date [{event.date_start.date()}] (YYYY-MM-DD): ") or None
    date_end = safe_input_date(f"New end date [{event.date_end.date()}] (YYYY-MM-DD): ") or None
    location = input(f"New location [{event.location}]: ").strip() or None
    attendees = safe_input_int(f"New attendees [{event.attendees}]: ") or None
    notes = input(f"New notes [{event.notes}]: ").strip() or None

    # Only gestion can change support contact
    support_contact_id = None
    if current_user.role.name == "gestion":
        support_users = session.query(Users).filter(Users.role.has(name="support")).all()
        print("\n📌 Available support contacts:")
        for u in support_users:
            print(f"ID: {u.id} | {u.first_name} {u.last_name} | {u.email}")
        support_contact_id = safe_input_int(f"New support contact ID [{event.support_contact_id}]: ") or None

    updates = {
        "name": name,
        "date_start": date_start,
        "date_end": date_end,
        "location": location,
        "attendees": attendees,
        "notes": notes,
        "support_contact_id": support_contact_id
    }

    updated_event, error = update_event(session, event_id, updates, current_user)

    if error:
        print(error)
    else:
        print(f"✅ Event updated: {updated_event.name} (ID: {updated_event.id})")


################################################################################
# File: ./app/views/login.py
################################################################################

import os
from app.config import SessionLocal
from app.controllers.auth_controller import authenticate_user
from app.utils.jwt_handler import create_jwt_token

TOKEN_FILE = ".token"

def login():
    session = SessionLocal()
    print("== Connexion ==")
    login_input = input("Email ou nom d'utilisateur : ")
    password = input("Mot de passe : ")

    user, error = authenticate_user(session, login_input, password)

    if error:
        print("❌", error)
        return None

    token = create_jwt_token(user)

    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    print(f"✅ Bienvenue {user.first_name} ({user.role.name})")
    return user


################################################################################
# File: ./app/views/logout.py
################################################################################

import os

def logout():
    if os.path.exists(".token"):
        os.remove(".token")
        print("✅ Déconnexion réussie.")
    else:
        print("ℹ️ Aucun utilisateur connecté.")


################################################################################
# File: ./app/views/user_view.py
################################################################################

from app.config import SessionLocal
from app.controllers.user_controller import create_user, update_user
from app.utils.auth import jwt_required, role_required
from app.models import Users


@jwt_required
@role_required("gestion")
def create_user_view(current_user):
    if current_user.role.name != "gestion":
        print("⛔ Seul le département gestion peut créer un collaborateur.")
        return

    session = SessionLocal()

    print("\n=== Création d'un nouveau collaborateur ===")
    username = input("Nom d'utilisateur : ")
    first_name = input("Prénom : ")
    last_name = input("Nom : ")
    email = input("Email : ")
    password = input("Mot de passe : ")
    role_name = input("Rôle (gestion, commercial, support) : ")

    user, error = create_user(session, username, first_name, last_name, email, password, role_name)
    if error:
        print(error)
    else:
        print(f"✅ Utilisateur {user.first_name} créé avec succès.")


@jwt_required
@role_required("gestion")
def update_user_view(current_user):
    session = SessionLocal()

    print("\n=== Liste des collaborateurs ===")
    users = session.query(Users).all()
    for user in users:
        print(f"ID: {user.id} | Login: {user.username} | Rôle: {user.role.name}")

    print("\n=== Modification d'un collaborateur ===")
    user_id = input("ID de l'utilisateur à modifier : ")

    # Vérifie si l'ID est bien un nombre
    try:
        user_id = int(user_id)
    except ValueError:
        print("❌ L'ID doit être un nombre.")
        return

    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        print(f"❌ Aucun utilisateur trouvé avec ID {user_id}.")
        return

    print(f"Infos actuelles pour {user.username} :")
    print(f"- Username : {user.username}")
    print(f"- Prénom   : {user.first_name}")
    print(f"- Nom      : {user.last_name}")
    print(f"- Email    : {user.email}")
    print(f"- Rôle     : {user.role.name}")

    updates = {}

    username = input(f"Nouveau username [{user.username}] : ").strip()
    if username:
        updates['username'] = username

    first_name = input(f"Nouveau prénom [{user.first_name}] : ").strip()
    if first_name:
        updates['first_name'] = first_name

    last_name = input(f"Nouveau nom [{user.last_name}] : ").strip()
    if last_name:
        updates['last_name'] = last_name

    email = input(f"Nouvel email [{user.email}] : ").strip()
    if email:
        updates['email'] = email

    password = input(f"Nouveau mot de passe [laisser vide pour ne pas changer] : ").strip()
    if password:
        updates['password'] = password

    role_name = input(f"Nouveau rôle [{user.role.name}] : ").strip()
    if role_name:
        updates['role_name'] = role_name

    if not updates:
        print("❌ Aucun champ à modifier.")
        return

    updated_user, error = update_user(session, user_id, **updates)
    if error:
        print(error)
    else:
        print(f"✅ Collaborateur {updated_user.username} mis à jour avec succès.")


################################################################################
# File: ./tests_perso/main_test.py
################################################################################

from app.views.login import login
from app.views.client_view import show_all_clients
from app.views.contract_view import show_all_contracts
from app.views.event_view import show_all_events

def main():
    user = login()
    if not user:
        return
    
    show_all_clients()
    show_all_contracts()
    show_all_events()


if __name__ == "__main__":
    main()

################################################################################
# File: ./tests_perso/test_create_user.py
################################################################################

from app.views.user_view import create_user_view
from app.config import SessionLocal
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    
    create_user_view()


if __name__ == "__main__":
    main()

################################################################################
# File: ./tests_perso/test_jwt.py
################################################################################

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



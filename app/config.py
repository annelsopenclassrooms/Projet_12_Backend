from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()


# URL de connexion SQLite
DATABASE_URL = "sqlite:///epic_events.db"

# Moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session locale (utilisable dans les services, contrôleurs, etc.)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


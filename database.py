from app.config import engine
from app.models.base import Base


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")
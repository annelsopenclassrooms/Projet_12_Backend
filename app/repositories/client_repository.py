from sqlalchemy.orm import Session
from app.models import Clients

def get_all_clients(session: Session):
    return session.query(Clients).order_by(Clients.last_name).all()

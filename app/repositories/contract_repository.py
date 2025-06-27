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
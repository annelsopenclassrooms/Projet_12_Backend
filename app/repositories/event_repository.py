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
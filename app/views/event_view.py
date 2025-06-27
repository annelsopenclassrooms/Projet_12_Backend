from app.config import SessionLocal
from app.controllers.event_controller import list_all_events
from app.utils.auth import jwt_required

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

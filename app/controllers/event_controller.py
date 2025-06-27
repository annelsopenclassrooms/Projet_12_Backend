from app.services.event_service import get_all_events as service_get_all_events

def list_all_events(session):
    events = service_get_all_events(session)
    return events

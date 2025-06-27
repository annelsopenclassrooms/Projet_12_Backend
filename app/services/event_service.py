from app.repositories.event_repository import get_all_events as repo_get_all_events

def get_all_events(session):
    return repo_get_all_events(session)

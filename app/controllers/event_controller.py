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

    role = current_user.role.name

    # Restriction pour support : ne peut modifier que ses propres événements
    if role == "support" and event.support_contact_id != current_user.id:
        return None, "⛔ You are not allowed to update this event."

    # Champs autorisés par rôle
    allowed_fields_by_role = {
        "gestion": {"support_contact_id"},
        "support": {"name", "date_start", "date_end", "location", "attendees", "notes"},
    }

    allowed_fields = allowed_fields_by_role.get(role, set())

    # Appliquer les modifications autorisées uniquement
    for field, value in updates.items():
        if value is not None:
            if field in allowed_fields:
                setattr(event, field, value)
            else:
                return None, f"⛔ You are not allowed to modify '{field}' as a '{role}'."

    session.commit()
    return event, None



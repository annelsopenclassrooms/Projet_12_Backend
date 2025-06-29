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

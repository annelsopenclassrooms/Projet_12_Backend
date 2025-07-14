from app.config import SessionLocal
from app.controllers.event_controller import list_all_events
from app.models import Clients, Contracts, Users, Events
from app.controllers.event_controller import create_event
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_date
from app.controllers.event_controller import update_event
from datetime import datetime, timedelta
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt

console = Console()


@jwt_required
def show_all_events_view(user):
    session = SessionLocal()
    events = list_all_events(session)

    if not events:
        console.print("[red]Aucun événement trouvé.[/red]")
        return

    table = Table(title=f"📋 Événements accessibles par {user.first_name}", header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nom", style="green")
    table.add_column("Client", style="yellow")
    table.add_column("Début", style="blue")
    table.add_column("Fin", style="blue")
    table.add_column("Lieu", style="cyan")
    table.add_column("Participants", justify="right")
    table.add_column("Support")

    for e in events:
        support = f"{e.support_contact.first_name} {e.support_contact.last_name}" if e.support_contact else "Aucun"
        client = f"{e.client.company_name}"
        table.add_row(
            str(e.id),
            e.name,
            client,
            e.date_start.strftime("%Y-%m-%d"),
            e.date_end.strftime("%Y-%m-%d"),
            e.location,
            str(e.attendees),
            support,
        )

    console.print(table)

@jwt_required
@role_required("commercial")
def create_event_view(current_user):
    session = SessionLocal()
    console.print("\n[bold cyan]=== Création d’un nouvel événement ===[/bold cyan]")

    # Affichage des clients
    clients = session.query(Clients).all()
    table = Table(title="📌 Clients existants", header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nom")
    table.add_column("Email")
    table.add_column("Entreprise")

    for c in clients:
        table.add_row(str(c.id), f"{c.first_name} {c.last_name}", c.email, c.company_name)
    console.print(table)

    client_id = safe_input_int("Client ID: ")

    # Affichage des contrats
    contracts = session.query(Contracts).filter_by(client_id=client_id).all()
    if not contracts:
        console.print(f"[red]❌ Aucun contrat trouvé pour le client ID {client_id}.[/red]")
        return

    contract_table = Table(title="📌 Contrats du client", header_style="bold magenta")
    contract_table.add_column("ID", justify="right")
    contract_table.add_column("Montant total")
    contract_table.add_column("Signé")

    for c in contracts:
        contract_table.add_row(str(c.id), f"{c.total_amount:.2f}", "Oui" if c.is_signed else "Non")
    console.print(contract_table)

    contract_id = safe_input_int("Contract ID: ")

    # Vérification que le contrat est signé
    selected_contract = session.query(Contracts).filter_by(id=contract_id, client_id=client_id).first()
    if not selected_contract:
        console.print(f"[red]❌ Contrat ID {contract_id} introuvable pour ce client.[/red]")
        return
    if not selected_contract.is_signed:
        console.print(f"[red]❌ Le contrat ID {contract_id} n'est pas signé. Impossible de créer un événement.[/red]")
        return

    # Affichage des contacts support
    support_users = session.query(Users).filter(Users.role.has(name="support")).all()
    support_table = Table(title="📌 Contacts support disponibles", header_style="bold magenta")
    support_table.add_column("ID", justify="right")
    support_table.add_column("Nom")
    support_table.add_column("Email")

    for s in support_users:
        support_table.add_row(str(s.id), f"{s.first_name} {s.last_name}", s.email)
    console.print(support_table)

    support_contact_id = safe_input_int("Support contact ID: ")
    name = input("Event name: ").strip()
    date_start = safe_input_date("Start date (YYYY-MM-DD): ")
    date_end = safe_input_date("End date (YYYY-MM-DD): ")
    location = input("Location: ").strip()
    attendees = safe_input_int("Number of attendees: ")
    notes = input("Notes: ").strip()

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
        console.print(f"[red]❌ {error}[/red]")
    else:
        console.print(f"[green]✅ Événement créé : {event.name} (ID: {event.id})[/green]")

@jwt_required
@role_required("gestion", "support")
def update_event_view(current_user):
    session = SessionLocal()

    console.print("\n[bold cyan]=== Mise à jour d'un événement ===[/bold cyan]")

    # Affichage des événements existants
    events = session.query(Events).all()
    if not events:
        console.print("[yellow]⚠️ Aucun événement trouvé.[/yellow]")
        return

    table = Table(title="📋 Événements existants", show_lines=True)
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Nom", style="bold")
    table.add_column("Client", style="green")
    table.add_column("Support", style="magenta")

    for event in events:
        client_name = f"{event.client.first_name} {event.client.last_name}"
        support_name = (
            f"{event.support_contact.first_name} {event.support_contact.last_name}"
            if event.support_contact else "Aucun"
        )
        table.add_row(str(event.id), event.name, client_name, support_name)

    console.print(table)

    event_id = safe_input_int("\nEntrez l'ID de l'événement à modifier : ")

    event = session.query(Events).filter_by(id=event_id).first()
    if not event:
        console.print("[red]❌ Événement non trouvé.[/red]")
        return

    # Restriction pour le support : uniquement ses propres événements
    if current_user.role.name == "support" and event.support_contact_id != current_user.id:
        console.print("[red]⛔ Vous n'êtes pas autorisé(e) à modifier cet événement.[/red]")
        return

    console.print(f"\n[bold]Infos actuelles pour l'événement ID {event.id}[/bold]")
    console.print(f"- Nom        : {event.name}")
    console.print(f"- Début      : {event.date_start}")
    console.print(f"- Fin        : {event.date_end}")
    console.print(f"- Lieu       : {event.location}")
    console.print(f"- Participants : {event.attendees}")
    console.print(f"- Notes      : {event.notes}")
    console.print(f"- Support ID : {event.support_contact_id}")

    updates = {}

    if current_user.role.name == "support":
        name = input(f"Nouveau nom [{event.name}] : ").strip() or None
        date_start_input = input(f"Nouvelle date de début [{event.date_start.date()}] (YYYY-MM-DD) : ").strip()
        date_start = safe_input_date("Date de début : ") if date_start_input else None

        date_end_input = input(f"Nouvelle date de fin [{event.date_end.date()}] (YYYY-MM-DD) : ").strip()
        date_end = safe_input_date("Date de fin : ") if date_end_input else None

        location = input(f"Nouveau lieu [{event.location}] : ").strip() or None
        attendees_input = input(f"Nombre de participants [{event.attendees}] : ").strip()
        attendees = int(attendees_input) if attendees_input.isdigit() else None
        notes = input(f"Nouvelles notes [{event.notes}] : ").strip() or None

        updates.update({
            "name": name,
            "date_start": date_start,
            "date_end": date_end,
            "location": location,
            "attendees": attendees,
            "notes": notes,
        })

    elif current_user.role.name == "gestion":
        support_users = session.query(Users).filter(Users.role.has(name="support")).all()
        table = Table(title="📌 Contacts support disponibles", show_lines=True)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Nom")
        table.add_column("Email", style="green")

        for user in support_users:
            full_name = f"{user.first_name} {user.last_name}"
            table.add_row(str(user.id), full_name, user.email)

        console.print(table)

        support_contact_id = safe_input_int(f"ID du nouveau support [{event.support_contact_id}] : ") or None
        updates["support_contact_id"] = support_contact_id

    updated_event, error = update_event(session, event_id, updates, current_user)

    if error:
        console.print(f"[red]❌ {error}[/red]")
    else:
        console.print(f"[green]✅ Événement mis à jour : {updated_event.name} (ID: {updated_event.id})[/green]")


@jwt_required
@role_required("gestion", "support")
def filter_events_view(user):
    session = SessionLocal()

    console.print("[bold cyan]📌 Filtrage avancé des événements[/bold cyan]")

    filters = [
        ("1", "Événements à venir"),
        ("2", "Événements passés"),
        ("3", "Sans support"),
        ("4", "Avec support"),
        ("5", "Plus de 100 participants"),
        ("0", "Retour"),
    ]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Choix")
    table.add_column("Filtre")

    for choice, label in filters:
        table.add_row(choice, label)

    console.print(table)

    choice = Prompt.ask("Votre choix", choices=[f[0] for f in filters], default="0")

    if choice == "0":
        return

    query = session.query(Events)

    now = datetime.now()

    if choice == "1":
        query = query.filter(Events.date_start > now)
    elif choice == "2":
        query = query.filter(Events.date_end < now)
    elif choice == "3":
        query = query.filter(Events.support_contact_id == None)
    elif choice == "4":
        query = query.filter(Events.support_contact_id != None)
    elif choice == "5":
        query = query.filter(Events.attendees > 100)

    events = query.all()

    if not events:
        console.print("[yellow]⚠️ Aucun événement trouvé pour ce filtre.[/yellow]")
    else:
        table = Table(title="📋 Événements filtrés", show_lines=True)
        table.add_column("ID")
        table.add_column("Nom")
        table.add_column("Client ID")
        table.add_column("Support")
        table.add_column("Date début")
        table.add_column("Participants")

        for event in events:
            support = str(event.support_contact_id) if event.support_contact_id else "Aucun"
            table.add_row(
                str(event.id),
                event.name,
                str(event.client_id),
                support,
                event.date_start.strftime("%Y-%m-%d %H:%M"),
                str(event.attendees or 0),
            )

        console.print(table)

    session.close()
    console.print("\n[bold cyan]Appuyez sur Entrée pour revenir...[/bold cyan]")
    input()
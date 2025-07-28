from app.config import SessionLocal
from app.controllers.event_controller import list_all_events, create_event, update_event
from app.models import Clients, Contracts, Users, Events
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_date
from app.views.user_view import show_all_users_view
from datetime import datetime, timedelta
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

@jwt_required
def show_all_events_view(current_user, *args, **kwargs):
    """Affiche tous les événements accessibles"""
    session = SessionLocal()
    try:
        events = list_all_events(session)

        if not events:
            console.print("[yellow]Aucun événement trouvé.[/yellow]")
            return

        table = Table(
            title=f"📋 Événements accessibles par {current_user.first_name}",
            header_style="bold magenta"
        )
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Nom", style="green")
        table.add_column("Client", style="yellow")
        table.add_column("Dates", style="blue")
        table.add_column("Lieu", style="cyan")
        table.add_column("Participants", justify="right")
        table.add_column("Support")

        for event in events:
            support = f"{event.support_contact.first_name} {event.support_contact.last_name}" if event.support_contact else "Aucun"
            dates = f"{event.date_start.strftime('%d/%m')} → {event.date_end.strftime('%d/%m/%Y')}"
            table.add_row(
                str(event.id),
                event.name,
                event.client.company_name,
                dates,
                event.location,
                str(event.attendees),
                support
            )

        console.print(table)
    finally:
        session.close()

@jwt_required
@role_required("commercial")
def create_event_view(current_user, *args, **kwargs):
    """Crée un nouvel événement"""
    session = SessionLocal()
    try:
        console.print("\n[bold cyan]=== Création d'un événement ===[/bold cyan]")

        # Sélection du client
        clients = session.query(Clients).all()
        client_table = Table(title="📌 Clients disponibles", header_style="bold blue")
        client_table.add_column("ID", justify="right")
        client_table.add_column("Nom")
        client_table.add_column("Entreprise")
        
        for client in clients:
            client_table.add_row(
                str(client.id),
                f"{client.first_name} {client.last_name}",
                client.company_name
            )
        console.print(client_table)

        client_id = safe_input_int("ID du client : ")
        if not client_id:
            return

        # Vérification des contrats signés
        contracts = session.query(Contracts).filter(
            Contracts.client_id == client_id,
            Contracts.is_signed == True
        ).all()

        if not contracts:
            console.print("[red]Ce client n'a aucun contrat signé.[/red]")
            return

        contract_table = Table(title="📌 Contrats signés disponibles", header_style="bold blue")
        contract_table.add_column("ID", justify="right")
        contract_table.add_column("Montant")
        contract_table.add_column("Créé le")
        
        for contract in contracts:
            contract_table.add_row(
                str(contract.id),
                f"{contract.total_amount:.2f} €",
                contract.date_created.strftime("%d/%m/%Y")
            )
        console.print(contract_table)

        contract_id = safe_input_int("ID du contrat : ")
        if not contract_id:
            return

        # Sélection du support (optionnel)
        support_users = session.query(Users).filter(Users.role.has(name="support")).all()
        support_table = Table(title="📌 Contacts support", header_style="bold blue")
        support_table.add_column("ID", justify="right")
        support_table.add_column("Nom")
        
        for user in support_users:
            support_table.add_row(str(user.id), f"{user.first_name} {user.last_name}")
        console.print(support_table)

        support_id = safe_input_int("ID du support (laisser vide si aucun) : ", optional=True)

        # Saisie des détails
        name = Prompt.ask("Nom de l'événement")
        date_start = safe_input_date("Date de début (JJ/MM/AAAA) : ")
        date_end = safe_input_date("Date de fin (JJ/MM/AAAA) : ")
        location = Prompt.ask("Lieu")
        attendees = safe_input_int("Nombre de participants : ")
        notes = Prompt.ask("Notes (optionnel) : ", default="")

        # Validation des dates
        if date_end < date_start:
            console.print("[red]La date de fin doit être après la date de début.[/red]")
            return

        # Confirmation
        console.print("\n[bold]Récapitulatif :[/bold]")
        console.print(f"- Client: {client_id}")
        console.print(f"- Contrat: {contract_id}")
        console.print(f"- Nom: {name}")
        console.print(f"- Dates: {date_start.strftime('%d/%m/%Y')} → {date_end.strftime('%d/%m/%Y')}")
        console.print(f"- Participants: {attendees}")

        if Confirm.ask("\nConfirmer la création ?", default=True):
            event, error = create_event(
                session,
                name=name,
                contract_id=contract_id,
                client_id=client_id,
                support_contact_id=support_id,
                date_start=date_start,
                date_end=date_end,
                location=location,
                attendees=attendees,
                notes=notes
            )

            if error:
                console.print(f"[red]{error}[/red]")
            else:
                console.print(f"[green]✅ Événement créé (ID: {event.id})[/green]")
    finally:
        session.close()


def update_event_view(user):
    session = SessionLocal()
    updates = {}

    try:
        event_id = int(Prompt.ask("ID de l’événement à modifier", default="0"))
        event = session.query(Events).get(event_id)

        if not event:
            console.print("[red]Événement introuvable.[/red]")
            return

        console.print(f"[bold]Événement actuel :[/bold] {event.name}")

        if user.role.name == "support":
            updates["name"] = Prompt.ask("Nom de l’événement", default=event.name)
            updates["date_start"] = safe_input_date("Date de début", default=event.date_start)
            updates["date_end"] = safe_input_date("Date de fin", default=event.date_end)
            updates["location"] = Prompt.ask("Lieu", default=event.location)
            updates["attendees"] = int(Prompt.ask("Nombre de participants", default=str(event.attendees)))
            updates["notes"] = Prompt.ask("Notes", default=event.notes)

        elif user.role.name == "gestion":
            #support_users = session.query(Users).filter_by(role="support").all()
            show_all_users_view()
            updates["support_contact_id"] = int(Prompt.ask("ID du support à affecter"))

        confirm = Confirm.ask("Confirmer la mise à jour ?", default=True)

        if confirm:
            updated_event, error = update_event(session, event.id, updates, user)
            if error:
                console.print(f"[red]Erreur : {error}[/red]")
            else:
                console.print(f"[green]Événement mis à jour : {updated_event.name}[/green]")
        else:
            console.print("[yellow]Mise à jour annulée.[/yellow]")

    except Exception as e:
        console.print(f"[red]Erreur inattendue : {e}[/red]")
    finally:
        session.close()


@jwt_required
@role_required("gestion", "support")
def filter_events_view(current_user, *args, **kwargs):
    """Filtre les événements selon différents critères"""
    session = SessionLocal()
    try:
        console.print("\n[bold cyan]=== Filtrage des événements ===[/bold cyan]")

        filters = [
            ("1", "Événements à venir"),
            ("2", "Événements passés"),
            ("3", "Sans support assigné"),
            ("4", "Avec support assigné"),
            ("5", "Plus de 50 participants"),
            ("0", "Retour")
        ]

        filter_table = Table(title="🔍 Options de filtrage", header_style="bold magenta")
        filter_table.add_column("Choix")
        filter_table.add_column("Description")
        
        for choice, label in filters:
            filter_table.add_row(choice, label)
        console.print(filter_table)

        choice = Prompt.ask("Votre choix", choices=[f[0] for f in filters], default="0")
        if choice == "0":
            return

        # Construction de la requête
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
            query = query.filter(Events.attendees > 50)

        # Exécution
        events = query.order_by(Events.date_start).all()

        if not events:
            console.print("[yellow]Aucun événement trouvé avec ce filtre.[/yellow]")
            return

        # Affichage des résultats
        result_table = Table(
            title=f"📋 Résultats ({filters[int(choice)-1][1]})", 
            header_style="bold green"
        )
        result_table.add_column("ID", justify="right")
        result_table.add_column("Nom")
        result_table.add_column("Client")
        result_table.add_column("Dates")
        result_table.add_column("Support")
        result_table.add_column("Participants")
        
        for event in events:
            dates = f"{event.date_start.strftime('%d/%m')} → {event.date_end.strftime('%d/%m/%Y')}"
            support = f"{event.support_contact.first_name} {event.support_contact.last_name}" if event.support_contact else "Aucun"
            result_table.add_row(
                str(event.id),
                event.name,
                event.client.company_name,
                dates,
                support,
                str(event.attendees)
            )

        console.print(result_table)
        
        if Confirm.ask("\nVoir les détails d'un événement ?", default=False):
            event_id = safe_input_int("ID de l'événement : ")
            if event_id:
                event = session.query(Events).get(event_id)
                if event:
                    console.print(f"\n[bold]Détails de l'événement ID {event.id}[/bold]")
                    console.print(f"- Nom: {event.name}")
                    console.print("f- Client: {event.client.company_name}")
                    console.print(f"- Dates: {event.date_start.strftime('%d/%m/%Y %H:%M')} → {event.date_end.strftime('%d/%m/%Y %H:%M')}")
                    console.print(f"- Lieu: {event.location}")
                    console.print(f"- Participants: {event.attendees}")
                    console.print(f"- Notes: {event.notes or 'Aucune'}")
                    console.print(f"- Support: {event.support_contact.first_name + ' ' + event.support_contact.last_name if event.support_contact else 'Aucun'}")
    finally:
        session.close()
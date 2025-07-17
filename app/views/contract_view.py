from app.config import SessionLocal
from app.controllers.contract_controller import list_all_contracts, create_contract, update_contract
from app.models import Clients, Users, Contracts
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_float, safe_input_yes_no
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime
from sqlalchemy import or_

console = Console()

@jwt_required
def show_all_contracts_view(current_user, *args, **kwargs):
    """Affiche tous les contrats accessibles"""
    session = SessionLocal()
    try:
        contracts = list_all_contracts(session)

        if not contracts:
            console.print("[yellow]Aucun contrat trouvé.[/yellow]")
            return

        table = Table(title=f"📋 Contrats accessibles par {current_user.first_name}", 
                     show_lines=True, header_style="bold magenta")
        table.add_column("ID", justify="right")
        table.add_column("Client", style="cyan")
        table.add_column("Signé", justify="center")
        table.add_column("Montant dû", justify="right")
        table.add_column("Montant total", justify="right")
        table.add_column("Créé le", style="dim")

        for contract in contracts:
            table.add_row(
                str(contract.id),
                f"{contract.client.first_name} {contract.client.last_name}",
                "✅" if contract.is_signed else "❌",
                f"{contract.amount_due:.2f}",
                f"{contract.total_amount:.2f}",
                str(contract.date_created.date())
            )

        console.print(table)
    finally:
        session.close()

@jwt_required
@role_required("gestion", "commercial")
def create_contract_view(current_user, *args, **kwargs):
    """Crée un nouveau contrat"""
    session = SessionLocal()
    try:
        console.print("\n[bold cyan]=== Créer un nouveau contrat ===[/bold cyan]")

        # Liste des clients
        clients = session.query(Clients).all()
        client_table = Table(title="📌 Clients disponibles", header_style="bold blue")
        client_table.add_column("ID", justify="right")
        client_table.add_column("Nom complet")
        client_table.add_column("Entreprise")
        client_table.add_column("Email")

        for client in clients:
            client_table.add_row(
                str(client.id),
                f"{client.first_name} {client.last_name}",
                client.company_name,
                client.email
            )

        console.print(client_table)
        client_id = safe_input_int("ID du client : ")

        # Liste des commerciaux (sauf pour la gestion)
        if current_user.role.name == "commercial":
            commercial_id = current_user.id
        else:
            commercials = session.query(Users).filter_by(role_id=2).all()
            comm_table = Table(title="📌 Commerciaux disponibles", header_style="bold blue")
            comm_table.add_column("ID", justify="right")
            comm_table.add_column("Nom complet")
            comm_table.add_column("Email")

            for c in commercials:
                comm_table.add_row(
                    str(c.id),
                    f"{c.first_name} {c.last_name}",
                    c.email
                )

            console.print(comm_table)
            commercial_id = safe_input_int("ID du commercial : ")

        # Saisie des montants
        total_amount = safe_input_float("Montant total du contrat : ")
        amount_due = safe_input_float("Montant restant dû : ")
        
        while amount_due > total_amount:
            console.print("[red]❌ Le montant dû ne peut pas être supérieur au montant total.[/red]")
            amount_due = safe_input_float("Montant restant dû : ")

        is_signed = Confirm.ask("Le contrat est-il signé ?", default=False)

        # Confirmation
        console.print("\n[bold]Récapitulatif du contrat :[/bold]")
        console.print(f"- Client ID: {client_id}")
        console.print(f"- Commercial ID: {commercial_id}")
        console.print(f"- Montant total: {total_amount:.2f}")
        console.print(f"- Montant dû: {amount_due:.2f}")
        console.print(f"- Signé: {'Oui' if is_signed else 'Non'}")

        if Confirm.ask("\nConfirmer la création ?", default=True):
            contract, error = create_contract(
                session, 
                client_id, 
                commercial_id, 
                total_amount, 
                amount_due, 
                is_signed
            )

            if error:
                console.print(f"[red]❌ {error}[/red]")
            else:
                console.print(f"[green]✅ Contrat créé avec succès : ID {contract.id}[/green]")
    finally:
        session.close()

@jwt_required
@role_required("gestion", "commercial")
def update_contract_view(current_user, *args, **kwargs):
    """Modifie un contrat existant"""
    session = SessionLocal()
    try:
        console.print("\n[bold cyan]=== Modifier un contrat existant ===[/bold cyan]")

        # Filtrage selon le rôle
        if current_user.role.name == "commercial":
            contracts = session.query(Contracts).join(Clients).filter(
                Clients.commercial_id == current_user.id
            ).all()
        else:
            contracts = session.query(Contracts).all()

        if not contracts:
            console.print("[yellow]Aucun contrat disponible pour modification.[/yellow]")
            return

        # Affichage liste
        contract_table = Table(title="📌 Contrats disponibles", header_style="bold blue")
        contract_table.add_column("ID", justify="right")
        contract_table.add_column("Client")
        contract_table.add_column("Montant total", justify="right")
        contract_table.add_column("Signé", justify="center")

        for contract in contracts:
            contract_table.add_row(
                str(contract.id),
                f"{contract.client.first_name} {contract.client.last_name}",
                f"{contract.total_amount:.2f}",
                "✅" if contract.is_signed else "❌"
            )

        console.print(contract_table)
        contract_id = safe_input_int("\nID du contrat à modifier : ")

        # Récupération contrat
        contract = session.query(Contracts).get(contract_id)
        if not contract:
            console.print(f"[red]❌ Contrat avec ID {contract_id} introuvable.[/red]")
            return

        # Vérification des permissions
        if (current_user.role.name == "commercial" and 
            contract.client.commercial_id != current_user.id):
            console.print("[red]❌ Vous n'avez pas accès à ce contrat.[/red]")
            return

        # Affichage détails
        detail_table = Table(title=f"📝 Détails du contrat ID {contract.id}", 
                           show_header=False)
        detail_table.add_column("Champ", style="cyan")
        detail_table.add_column("Valeur")

        detail_table.add_row("Client", f"{contract.client.first_name} {contract.client.last_name}")
        detail_table.add_row("Commercial", f"{contract.client.commercial.first_name} {contract.client.commercial.last_name}")
        detail_table.add_row("Montant total", f"{contract.total_amount:.2f}")
        detail_table.add_row("Montant dû", f"{contract.amount_due:.2f}")
        detail_table.add_row("Signé", "✅ Oui" if contract.is_signed else "❌ Non")

        console.print(detail_table)

        # Saisie modifications
        updates = {
            "total_amount": safe_input_float(
                "Nouveau montant total", 
                default=contract.total_amount
            ),
            "amount_due": safe_input_float(
                "Nouveau montant dû", 
                default=contract.amount_due
            ),
            "is_signed": Confirm.ask(
                "Le contrat est-il signé ?", 
                default=contract.is_signed
            )
        }

        # Validation montant dû
        while updates["amount_due"] > updates["total_amount"]:
            console.print("[red]❌ Le montant dû ne peut dépasser le montant total.[/red]")
            updates["amount_due"] = safe_input_float(
                "Nouveau montant dû", 
                default=contract.amount_due
            )

        # Confirmation
        if Confirm.ask("\n[bold]Confirmer la modification ?[/bold]", default=True):
            updated_contract, error = update_contract(
                session, 
                contract_id, 
                updates, 
                current_user
            )

            if error:
                console.print(f"[red]❌ {error}[/red]")
            else:
                console.print(f"[green]✅ Contrat ID {updated_contract.id} mis à jour avec succès.[/green]")
        else:
            console.print("[yellow]Modification annulée.[/yellow]")
    finally:
        session.close()

@jwt_required
@role_required("gestion", "commercial")
def filter_contracts_view(current_user, *args, **kwargs):
    """Filtre les contrats selon différents critères"""
    session = SessionLocal()
    try:
        console.print("\n[bold cyan]=== Filtrer les contrats ===[/bold cyan]")

        # Menu des filtres
        filters = {
            "1": ("Contrats non signés", Contracts.is_signed == False),
            "2": ("Contrats non entièrement payés", Contracts.amount_due > 0),
            "3": ("Contrats non signés ET non payés", 
                 (Contracts.is_signed == False, Contracts.amount_due > 0)),
            "4": ("Contrats signés", Contracts.is_signed == True),
            "5": ("Contrats entièrement payés", Contracts.amount_due == 0)
        }

        table = Table(title="🔍 Filtres disponibles", header_style="bold magenta")
        table.add_column("Choix", style="dim")
        table.add_column("Description")

        for key, (desc, _) in filters.items():
            table.add_row(key, desc)
        table.add_row("0", "[red]Retour[/red]")

        console.print(table)

        choice = Prompt.ask("Votre choix", choices=["0", "1", "2", "3", "4", "5"], default="0")

        if choice == "0":
            return

        # Construction de la requête
        query = session.query(Contracts)
        
        # Filtre par rôle
        if current_user.role.name == "commercial":
            query = query.join(Clients).filter(Clients.commercial_id == current_user.id)

        # Application du filtre
        filter_cond = filters[choice][1]
        if isinstance(filter_cond, tuple):
            query = query.filter(*filter_cond)
        else:
            query = query.filter(filter_cond)

        # Exécution
        results = query.order_by(Contracts.date_created.desc()).all()

        if not results:
            console.print("[yellow]Aucun contrat trouvé avec ce filtre.[/yellow]")
            return

        # Affichage résultats
        result_table = Table(title=f"📋 Résultats - {filters[choice][0]}", 
                           show_lines=True, header_style="bold green")
        result_table.add_column("ID", justify="right")
        result_table.add_column("Client")
        result_table.add_column("Commercial")
        result_table.add_column("Total", justify="right")
        result_table.add_column("Dû", justify="right")
        result_table.add_column("Signé", justify="center")
        result_table.add_column("Créé le", style="dim")

        for contract in results:
            result_table.add_row(
                str(contract.id),
                f"{contract.client.first_name} {contract.client.last_name}",
                f"{contract.client.commercial.first_name} {contract.client.commercial.last_name}",
                f"{contract.total_amount:.2f}",
                f"{contract.amount_due:.2f}",
                "✅" if contract.is_signed else "❌",
                contract.date_created.strftime("%Y-%m-%d")
            )

        console.print(result_table)
    finally:
        session.close()
from app.config import SessionLocal
from app.controllers.contract_controller import list_all_contracts, create_contract, update_contract
from app.models import Clients, Users, Contracts
from app.utils.auth import jwt_required, role_required
from app.utils.helpers import safe_input_int, safe_input_float, safe_input_yes_no

from rich.console import Console
from rich.table import Table

console = Console()


@jwt_required
def show_all_contracts_view(user):
    session = SessionLocal()
    contracts = list_all_contracts(session)

    if not contracts:
        console.print("[yellow]Aucun contract trouvé.[/yellow]")
        return

    table = Table(title=f"📋 Contracts accessibles par {user.first_name}", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Client", style="cyan")
    table.add_column("Signé", justify="center")
    table.add_column("Montant dû", justify="right")
    table.add_column("Créé le", style="dim")
    table.add_column("Prénom Client", style="magenta")
    table.add_column("Nom client", style="magenta")

    for contract in contracts:
        table.add_row(
            str(contract.id),
            contract.client.company_name,
            "✅" if contract.is_signed else "❌",
            f"{contract.amount_due:.2f}",
            str(contract.date_created.date()),
            contract.client.first_name,
            contract.client.last_name
        )

    console.print(table)

@jwt_required
@role_required("gestion", "commercial")
def create_contract_view(current_user):
    session = SessionLocal()

    console.print("\n[bold cyan]=== Créer un nouveau contrat ===[/bold cyan]")

    # Liste des clients
    clients = session.query(Clients).all()
    client_table = Table(title="📌 Clients disponibles")
    client_table.add_column("ID", justify="right")
    client_table.add_column("Nom")
    client_table.add_column("Email")

    for client in clients:
        client_table.add_row(
            str(client.id),
            f"{client.first_name} {client.last_name}",
            client.email
        )

    console.print(client_table)
    client_id = safe_input_int("ID du client : ")

    # Liste des commerciaux
    commercials = session.query(Users).filter_by(role_id=2).all()
    comm_table = Table(title="📌 Commerciaux disponibles")
    comm_table.add_column("ID", justify="right")
    comm_table.add_column("Nom")
    comm_table.add_column("Email")

    for c in commercials:
        comm_table.add_row(
            str(c.id),
            f"{c.first_name} {c.last_name}",
            c.email
        )

    console.print(comm_table)
    commercial_id = safe_input_int("ID du commercial : ")

    # Montants avec validation
    total_amount = safe_input_float("Montant total du contrat : ")

    while True:
        amount_due = safe_input_float("Montant restant dû : ")
        if amount_due <= total_amount:
            break
        console.print("[red]❌ Le montant dû ne peut pas être supérieur au montant total.[/red]")

    is_signed = safe_input_yes_no("Le contrat est-il signé ? (y/n) [n] : ", default=False)

    contract, error = create_contract(session, client_id, commercial_id, total_amount, amount_due, is_signed)

    if error:
        console.print(f"[red]❌ {error}[/red]")
    else:
        console.print(f"[green]✅ Contrat créé avec succès : ID {contract.id} pour {contract.client.first_name} {contract.client.last_name}[/green]")


@jwt_required
@role_required("gestion", "commercial")
def update_contract_view(current_user):
    session = SessionLocal()

    console.print("\n[bold cyan]=== Modifier un contrat existant ===[/bold cyan]")

    contracts = session.query(Contracts).all()
    contract_table = Table(title="📌 Contrats existants")
    contract_table.add_column("ID", justify="right")
    contract_table.add_column("Client")
    contract_table.add_column("Montant total", justify="right")
    contract_table.add_column("Signé", justify="center")

    for contract in contracts:
        client_name = f"{contract.client.first_name} {contract.client.last_name}"
        contract_table.add_row(
            str(contract.id),
            client_name,
            f"{contract.total_amount:.2f}",
            "✅" if contract.is_signed else "❌"
        )

    console.print(contract_table)
    contract_id = safe_input_int("\nID du contrat à modifier : ")

    contract = session.query(Contracts).filter_by(id=contract_id).first()
    if not contract:
        console.print(f"[red]❌ Contrat avec ID {contract_id} introuvable.[/red]")
        return

    detail_table = Table(title=f"📝 Détails du contrat ID {contract.id}")
    detail_table.add_column("Champ")
    detail_table.add_column("Valeur")

    detail_table.add_row("Client", f"{contract.client.first_name} {contract.client.last_name}")
    detail_table.add_row("Commercial ID", str(contract.commercial_id))
    detail_table.add_row("Montant total", f"{contract.total_amount:.2f}")
    detail_table.add_row("Montant dû", f"{contract.amount_due:.2f}")
    detail_table.add_row("Signé", "✅ Oui" if contract.is_signed else "❌ Non")

    console.print(detail_table)

    # --- Demande des nouvelles valeurs, saut possible avec Entrée ---
    total_input = input(f"Nouveau montant total [{contract.total_amount}]: ").strip()
    total_amount = float(total_input) if total_input else contract.total_amount

    while True:
        due_input = input(f"Nouveau montant dû [{contract.amount_due}]: ").strip()
        if not due_input:
            amount_due = contract.amount_due
            break

        try:
            amount_due = float(due_input)
        except ValueError:
            console.print("[red]⛔ Veuillez entrer un nombre valide.[/red]")
            continue

        if amount_due > total_amount:
            console.print("[red]❌ Le montant dû ne peut pas dépasser le montant total.[/red]")
        else:
            break

    is_signed = safe_input_yes_no(
        f"Le contrat est-il signé (y/n) [actuellement {'Oui' if contract.is_signed else 'Non'}] : ",
        default=contract.is_signed
    )

    updates = {
        "total_amount": total_amount,
        "amount_due": amount_due,
        "is_signed": is_signed
    }

    updated_contract, error = update_contract(session, contract_id, updates, current_user)

    if error:
        console.print(f"[red]❌ {error}[/red]")
    else:
        console.print(f"[green]✅ Contrat mis à jour avec succès.[/green]")

from rich.console import Console
from app.utils.auth import jwt_required, role_required
from app.views.event_view import filter_events_view, update_event_view, show_all_events_view
from app.views.client_view import show_all_clients_view
from app.views.contract_view import show_all_contracts_view
from app.menus.utils import display_action_menu

console = Console()


@role_required("support")
def support_menu(user):
    actions = [
        ("1", "Afficher tous les clients", show_all_clients_view),
        ("2", "Afficher tous les contrats", show_all_contracts_view),
        ("3", "Afficher tous les événements", show_all_events_view),
        ("4", "Filtrer les événements qui vous sont attribués", filter_events_view),
        ("5", "Mettre à jour un événement dont vous êtes responsable", update_event_view),
        ("0", "[red]Quitter"),
    ]
    display_action_menu(actions)


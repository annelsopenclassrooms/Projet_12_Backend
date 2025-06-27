from app.views.login import login
from app.views.client_view import show_all_clients
from app.views.contract_view import show_all_contracts

def main():
    user = login()
    if not user:
        return
    
    show_all_clients()
    show_all_contracts()


if __name__ == "__main__":
    main()
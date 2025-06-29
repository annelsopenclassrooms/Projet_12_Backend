from app.views.contract_view import create_contract_view
from app.views.event_view import create_event_view
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    

    create_event_view()

if __name__ == "__main__":
    main()
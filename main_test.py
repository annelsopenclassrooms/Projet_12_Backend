from app.views.login import login
from app.views.client_view import show_all_clients

def main():
    user = login()
    if not user:
        return
    
    show_all_clients()

if __name__ == "__main__":
    main()
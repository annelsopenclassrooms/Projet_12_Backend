from app.views.user_view import create_user_view, update_user_view
from app.config import SessionLocal
from app.views.login import login

def main():
    user = login()
    if not user:
        return
    
    
    update_user_view()


if __name__ == "__main__":
    main()
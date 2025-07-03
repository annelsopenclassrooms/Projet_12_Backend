from app.views.login import login
from app.views.main_menu import main_menu


def main():
    user = login()
    if user:
        main_menu(user)


if __name__ == "__main__":
    main()

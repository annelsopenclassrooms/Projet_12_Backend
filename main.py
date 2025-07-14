from app.views.login import login
from app.menus.main_menu import main_menu
import sentry_sdk


def main():
    sentry_sdk.init(
        dsn="https://9e3789b7c2b1a67367ea058d3f20bc87@o4509668801773568.ingest.de.sentry.io/4509668806099024",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )
    
    user = login()
    if user:
        main_menu(user)


if __name__ == "__main__":
    main()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import Users
from app.models.role import Roles
from app.models.client import Clients
from app.models.event import Events
from app.models.contract import Contracts
from app.utils.security import hash_password

# --- Base de test en mémoire ---
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# --- Fixtures utilisateurs ---
@pytest.fixture
def role_commercial(session):
    role = Roles(name="Commercial")
    session.add(role)
    session.commit()
    return role

@pytest.fixture
def commercial_user(session, role_commercial):
    user = Users(
        username="john_doe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        hashed_password=hash_password("password123"),
        role_id=role_commercial.id,
    )
    session.add(user)
    session.commit()
    return user

# --- Fixtures clients ---
@pytest.fixture
def fake_clients(session, commercial_user):
    clients = [
        Clients(
            name="Client A",
            email="clientA@example.com",
            phone="0102030405",
            commercial_id=commercial_user.id
        ),
        Clients(
            name="Client B",
            email="clientB@example.com",
            phone="0607080910",
            commercial_id=commercial_user.id
        )
    ]
    session.add_all(clients)
    session.commit()
    return clients

# --- Fixtures contrats ---
@pytest.fixture
def fake_contracts(session, fake_clients):
    contracts = [
        Contracts(
            client_id=fake_clients[0].id,
            total_amount=1000,
            remaining_amount=200,
            status="pending"
        ),
        Contracts(
            client_id=fake_clients[1].id,
            total_amount=5000,
            remaining_amount=0,
            status="signed"
        )
    ]
    session.add_all(contracts)
    session.commit()
    return contracts

# --- Fixtures événements ---
@pytest.fixture
def fake_events(session, commercial_user, fake_clients):
    events = [
        Events(
            client_id=fake_clients[0].id,
            support_contact_id=commercial_user.id,
            event_name="Kickoff Meeting"
        )
    ]
    session.add_all(events)
    session.commit()
    return events

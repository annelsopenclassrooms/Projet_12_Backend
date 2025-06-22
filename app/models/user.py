from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    created_clients = relationship('Clients', back_populates='commercial')
    assigned_events = relationship('Events', back_populates='support_contact')

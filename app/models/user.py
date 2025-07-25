from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .mixins import EncryptedString

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(EncryptedString, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship('Roles')
    created_clients = relationship('Clients', back_populates='commercial')
    assigned_events = relationship('Events', back_populates='support_contact')

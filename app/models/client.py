from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .mixins import EncryptedString


class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(EncryptedString, unique=True, nullable=False)
    phone = Column(EncryptedString, nullable=False)
    company_name = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commercial_id = Column(Integer, ForeignKey('users.id'))
    commercial = relationship('Users', back_populates='created_clients')

    contracts = relationship('Contracts', back_populates='client')
    events = relationship('Events', back_populates='client')

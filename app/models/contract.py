from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Contracts(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    commercial_id = Column(Integer, ForeignKey('users.id'))

    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    client = relationship('Clients', back_populates='contracts')


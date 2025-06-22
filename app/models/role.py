# models/role.py
from sqlalchemy import Column, Integer, String
from .base import Base

class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
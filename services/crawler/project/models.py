"""Declare models and relationships."""
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from database import engine

Base = declarative_base()


class AccountMetric(Base):
    __tablename__ = "accountmetric"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    balance = Column(Integer)
    towerheight = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())


# Base.metadata.create_all(engine)

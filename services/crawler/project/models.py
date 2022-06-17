"""Declare models and relationships."""
from sqlalchemy import Column, DateTime, Integer, String, func, UniqueConstraint, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from database import session, engine

Base = declarative_base()


class AccountStat(Base):
    __tablename__ = "accountstat"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    balance = Column(Integer, nullable=False, default=0)
    towerheight = Column(Integer, nullable=False, default=0)
    proofsinepoch = Column(Integer, nullable=False, default=0)
    lastepochmined = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MinerHistory(Base):
    __tablename__ = "minerhistory"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    epoch = Column(Integer, nullable=False, default=0)
    proofssubmitted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('address', 'epoch', name='uc_address_epoch'),)

    # def update(self):
    #     mapped_values = {}
    #     for item in MinerHistory.__dict__.iteritems():
    #         field_name = item[0]
    #         field_type = item[1]
    #         is_column = isinstance(field_type, InstrumentedAttribute)
    #         if is_column:
    #             mapped_values[field_name] = getattr(self, field_name)
    #
    #     session.query(MinerHistory).filter(MinerHistory.id == self.id).update(mapped_values)
    #     session.commit()


class PaymentEvent(Base):
    __tablename__ = "paymentevent"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    height = Column(Integer, nullable=False, default=0)
    type = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    sender = Column(String(100))
    recipient = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChainEvent(Base):
    __tablename__ = "chainevent"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    height = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    type = Column(String(100), nullable=False, default="")
    status = Column(String(100), nullable=False, default="")
    sender = Column(String(100))
    recipient = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Epoch(Base):
    __tablename__ = "epoch"

    id = Column(Integer, primary_key=True)
    epoch = Column(Integer, nullable=False, unique=True)
    timestamp = Column(DateTime, nullable=True)
    height = Column(Integer, nullable=False)
    miners = Column(Integer, nullable=True)
    proofs = Column(Integer, nullable=True)
    minerspayable = Column(Integer, nullable=True)
    minerspayableproofs = Column(Integer, nullable=True)
    validatorproofs = Column(Integer, nullable=True)
    minerpaymenttotal = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class NetworkStat(Base):
    __tablename__ = "networkstat"

    id = Column(Integer, primary_key=True)
    height = Column(Integer, nullable=False)
    epoch = Column(Integer, nullable=False)
    progress = Column(Float, nullable=False)
    totalsupply = Column(Integer, nullable=False)
    totaladdresses = Column(Integer, nullable=False)
    totalminers = Column(Integer, nullable=False)
    activeminers = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Base.metadata.create_all(engine)

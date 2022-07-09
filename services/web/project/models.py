from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(
        db.String(200), primary_key=False, unique=False, nullable=False
    )

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.name)


class AccountStat(db.Model):
    __tablename__ = "accountstat"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    balance = db.Column(db.Integer, nullable=False, default=0)
    towerheight = db.Column(db.Integer, nullable=False, default=0)
    proofsinepoch = db.Column(db.Integer, nullable=False, default=0)
    lastepochmined = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<a href="https://0l.interblockcha.in/address/{self.address}">{self.address}</a>'


class MinerHistory(db.Model):
    __tablename__ = "minerhistory"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    epoch = db.Column(db.Integer, nullable=False, default=0)
    proofssubmitted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())


class PaymentEvent(db.Model):
    __tablename__ = "paymentevent"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=0)
    sender = db.Column(db.String(100))
    recipient = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())


class ChainEvent(db.Model):
    __tablename__ = "chainevent"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=True)
    type = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(100), nullable=True)
    sender = db.Column(db.String(100), nullable=True)
    recipient = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())


class Epoch(db.Model):
    __tablename__ = "epoch"

    id = db.Column(db.Integer, primary_key=True)
    epoch = db.Column(db.Integer, nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    height = db.Column(db.Integer, nullable=False)
    miners = db.Column(db.Integer, nullable=True)
    proofs = db.Column(db.Integer, nullable=True)
    minerspayable = db.Column(db.Integer, nullable=True)
    minerspayableproofs = db.Column(db.Integer, nullable=True)
    validatorproofs = db.Column(db.Integer, nullable=True)
    minerpaymenttotal = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class NetworkStat(db.Model):
    __tablename__ = "networkstat"

    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer, nullable=False)
    epoch = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Float, nullable=False)
    totalsupply = db.Column(db.Integer, nullable=False)
    totaladdresses = db.Column(db.Integer, nullable=False)
    totalminers = db.Column(db.Integer, nullable=False)
    activeminers = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class EventLog(db.Model):
    __tablename__ = "eventlog"

    id = db.Column(db.Integer, primary_key=True)
    event_source = db.Column(db.String(500), nullable=True)
    type = db.Column(db.String(100), nullable=True)
    subject = db.Column(db.String(1000), nullable=True)
    message = db.Column(db.String(5000), nullable=True)
    response = db.Column(db.String(5000), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

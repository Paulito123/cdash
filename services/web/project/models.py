from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=False)
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


class AccountMetric(db.Model):
    __tablename__ = "accountmetric"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    balance = db.Column(db.Integer)
    towerheight = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            self.address,
            self.name,
            self.balance,
            self.towerheight)

from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import FlaskGroup
from project import create_app, db
from project.models import User, AccountMetric


app = create_app()
cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    u1 = User(
        email="bla@mail.com",
        name="Bla die Bla",
        password=generate_password_hash("SecretPassword", method='sha256'))
    u2 = User(
        email="foo@mail.com",
        name="Foo die Foo",
        password=generate_password_hash("SecretPassword", method='sha256'))
    db.session.add(u1)
    db.session.add(u2)

    a1 = AccountMetric(
        address="91185ED5A1976F2E01BE08EE96E4D9D2",
        name="Validator Acc 1",
        balance=0,
        towerheight=0)
    a2 = AccountMetric(
        address="59357260C14BC6576749D87EB627D727",
        name="Node account 1",
        balance=0,
        towerheight=0)

    db.session.add(a1)
    db.session.add(a2)
    db.session.commit()


if __name__ == "__main__":
    cli()

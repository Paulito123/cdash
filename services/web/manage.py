from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import FlaskGroup
from project import create_app, db
from project.models import User, AccountMetric
from secrets import SecretsDev
# from secrets_prod import SecretsProd


app = create_app()
cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    # for user in SecretsProd.user_list:
    for user in SecretsDev.user_list:
        u = User(
            email=f"{user['email']}",
            name=f"{user['name']}",
            password=generate_password_hash(f"{user['paswd']}", method='sha256'))
        db.session.add(u)

    counter = 1
    # for acnt in SecretsProd.account_list:
    for acnt in SecretsDev.account_list:
        a = AccountMetric(
            address=f"{acnt}",
            name=f"Account {counter}",
            balance=0,
            towerheight=0)
        db.session.add(a)
        counter = counter + 1

    db.session.commit()


if __name__ == "__main__":
    cli()

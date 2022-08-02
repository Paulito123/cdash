import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import FlaskGroup
from project import create_app, db
from project.models import User, AccountStat
# from secrets import SecretsDev
from secrets_prod import SecretsProd


app = create_app()
cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.engine.execute("DROP VIEW IF EXISTS vw_epoch_rich")
    db.engine.execute("DROP VIEW IF EXISTS vw_epoch_keys")
    db.drop_all()
    db.create_all()
    # views
    db.engine.execute("create or replace view vw_epoch_keys as select epoch, height, COALESCE(lag(height, 1) over (order by epoch desc), 999999999999) as pheight from epoch e")
    db.engine.execute("create or replace view vw_epoch_rich as with proofs as (select e.epoch, e.height, e.pheight, coalesce(sum(m.proofssubmitted), 0) as proofssubmitted from vw_epoch_keys e left join minerhistory m on m.epoch = e.epoch group by e.epoch, height, pheight ), payments as (select pr.epoch, pr.height, pr.proofssubmitted, sum(p.amount) as amount, count(distinct address) as accounts from proofs pr left join paymentevent p on p.height >= pr.height and p.height < pr.pheight and p.type = 'receivedpayment' group by pr.epoch, pr.height, pr.proofssubmitted), corrected as (select epoch, height, proofssubmitted, coalesce(lag(amount, 1) over (order by epoch desc), 0) as amount, coalesce(lag(accounts, 1) over (order by epoch desc), 0) as accounts from payments) select epoch, height, proofssubmitted as proofs, amount as rewards, accounts from corrected")
    # commit all
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    for user in SecretsProd.user_list:
        u = User(
            email=f"{user['email']}",
            name=f"{user['name']}",
            password=generate_password_hash(f"{user['paswd']}", method='sha256'),
            totp=f"{user['totp']}")
        db.session.add(u)

    counter = 1
    for acnt in SecretsProd.account_list:
        acc_nr = f"{counter}"
        acc_name = f"Account {acc_nr.zfill(2)}"
        a = AccountStat(
            address=f"{acnt}",
            name=f"{acc_name}",
            balance=0,
            towerheight=0)
        db.session.add(a)
        counter = counter + 1

    db.session.commit()


@cli.command("init_db")
def init_db():
    create_db()
    seed_db()


@cli.command("add_address")
@click.option("--addr")
@click.option("--name")
def add_address(addr="", name=""):
    # check is account is valid
    if len(addr) != 32 or len(name) == 0 or len(name) > 100:
        print("ERROR: address or name not valid!")
        return

    # check is account already exists
    acc_check = AccountStat.query.filter_by(address=addr).first()
    if acc_check:
        print("ERROR: account already exists!")
        return

    # insert new account
    a = AccountStat(address=f"{addr}",
                    name=f"{name}")
    db.session.add(a)
    db.session.commit()


if __name__ == "__main__":
    cli()

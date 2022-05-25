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
        email="wvv@mail.com",
        name="Wally",
        password=generate_password_hash("1234HoedjeVan@MoederGast791", method='sha256'))
    u2 = User(
        email="pjg@mail.com",
        name="Paulito",
        password=generate_password_hash("1234HoedjeVan@MoederGast791", method='sha256'))
    db.session.add(u1)
    db.session.add(u2)

    a1 = AccountMetric(
        address="2BFD96D8A674A360B733D16C65728D72",
        name="Account 1",
        balance=0,
        towerheight=0)
    a2 = AccountMetric(
        address="7019D164138F5E0B238E0464D0F60ABD",
        name="Account 2",
        balance=0,
        towerheight=0)
    a3 = AccountMetric(
        address="94BAA35B9EF311B3CD96BACBC6AA5372",
        name="Account 3",
        balance=0,
        towerheight=0)
    a4 = AccountMetric(
        address="6BDB4E6FAEDA56569ED371D5CCBB14B6",
        name="Account 4",
        balance=0,
        towerheight=0)
    a5 = AccountMetric(
        address="77DC471037ABB82228987C2752DAC131",
        name="Account 5",
        balance=0,
        towerheight=0)
    a6 = AccountMetric(
        address="6C29248CCC36C9AA101D92A4FEC81786",
        name="Account 6",
        balance=0,
        towerheight=0)
    a7 = AccountMetric(
        address="8BE9CD06D2B458FAD293BBDB74624368",
        name="Account 7",
        balance=0,
        towerheight=0)
    a8 = AccountMetric(
        address="5D4F887D36B356894C6CE36F243D54AE",
        name="Account 8",
        balance=0,
        towerheight=0)
    a9 = AccountMetric(
        address="A9BE247F465973A127CD9BC201AAB34C",
        name="Account 9",
        balance=0,
        towerheight=0)
    a10 = AccountMetric(
        address="0CB4FEF910B686E5AE39049FB892CB24",
        name="Account 10",
        balance=0,
        towerheight=0)
    a11 = AccountMetric(
        address="8A371A3655F880704107AEE47AAE50C9",
        name="Account 11",
        balance=0,
        towerheight=0)
    a12 = AccountMetric(
        address="A694929CDB6E9F520703DC35F393F65B",
        name="Account 12",
        balance=0,
        towerheight=0)
    a13 = AccountMetric(
        address="A8F15A2E8D986891C512FCEBC26FC083",
        name="Account 13",
        balance=0,
        towerheight=0)
    a14 = AccountMetric(
        address="AED1AB5E5DA40F61C92D00B85CF54902",
        name="Account 14",
        balance=0,
        towerheight=0)
    a15 = AccountMetric(
        address="6E3A0F7F148B65DC43F5E90288006D75",
        name="Account 15",
        balance=0,
        towerheight=0)
    a16 = AccountMetric(
        address="CF42ABA8D9F3D54EC0825401653C8BEA",
        name="Account 16",
        balance=0,
        towerheight=0)
    a17 = AccountMetric(
        address="555B737DFBF4BFFB1F6B001CF60638E2",
        name="Account 17",
        balance=0,
        towerheight=0)
    db.session.add(a1)
    db.session.add(a2)
    db.session.add(a3)
    db.session.add(a4)
    db.session.add(a5)
    db.session.add(a6)
    db.session.add(a7)
    db.session.add(a8)
    db.session.add(a9)
    db.session.add(a10)
    db.session.add(a11)
    db.session.add(a12)
    db.session.add(a13)
    db.session.add(a14)
    db.session.add(a15)
    db.session.add(a16)
    db.session.add(a17)
    db.session.commit()


if __name__ == "__main__":
    cli()

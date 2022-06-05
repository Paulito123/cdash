from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountStat, MinerHistory, PaymentEvent
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    rows = AccountStat.query.order_by(db.asc(AccountStat.name)).all()
    totalbalance = db.session.query(db.func.sum(AccountStat.balance)).scalar()
    totalheight = db.session.query(db.func.sum(AccountStat.towerheight)).scalar()
    nrofaccounts = db.session.query(db.func.count(AccountStat.address)).scalar()
    lastupdate = db.session.query(db.func.max(AccountStat.updated_at)).scalar()
    lastepochmined = db.session.query(db.func.max(AccountStat.lastepochmined)).scalar()
    prev_epoch = lastepochmined - 1
    avg_proofs_mined_last_epoch = round(db.engine.execute(f"select avg(proofssubmitted) as average from minerhistory where epoch = {prev_epoch}").scalar(), 2)
    rewards_last_epoch = round(db.engine.execute(
        f"select sum(pe.amount) from paymentevent pe join (select address, max(height) as height from paymentevent group by address) pe2 on pe.address = pe2.address and pe.height = pe2.height").scalar(), 2)
    test_data = [(1, 3), (2, 5), (3, 2), (4, 6), (5, 3), (6, 7)]
    labels = [row[0] for row in test_data]
    values = [row[1] for row in test_data]
    return render_template('dashboard.html',
                           name=current_user.name,
                           rows=rows,
                           totalbalance=totalbalance,
                           totalheight=totalheight,
                           lastupdate=lastupdate,
                           nrofaccounts=nrofaccounts,
                           lastepochmined=lastepochmined,
                           avg_proofs_mined_last_epoch=avg_proofs_mined_last_epoch,
                           rewards_last_epoch=rewards_last_epoch,
                           labels=labels,
                           values=values)

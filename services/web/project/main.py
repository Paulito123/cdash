from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountStat, MinerHistory, PaymentEvent
from .config import Config
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        name = current_user.name
    else:
        name = ""
    return render_template('index.html', name=name)


@main.route('/dashboard')
@login_required
def dashboard():
    address_url = Config.BASE_URL + "address/"
    rows = []
    totalbalance = 0
    totalheight = 0
    nrofaccounts = 0
    lastupdate = 0
    lastepochmined = 0
    avg_proofs_mined_last_epoch = 0
    rewards_last_epoch = 0
    proofs_submitted_last_epoch = 0
    reward_pp_last_epoch = 0
    chart_data = {}
    prev_epoch = 0
    miner_history = {}

    try:
        rows = AccountStat.query.order_by(db.asc(AccountStat.name)).all()

        q_result = db.session.query(db.func.sum(AccountStat.balance)).scalar()
        if q_result:
            totalbalance = round(q_result / 1000, 2)

        q_result = db.session.query(db.func.sum(AccountStat.towerheight)).scalar()
        if q_result:
            totalheight = q_result

        q_result = db.session.query(db.func.count(AccountStat.address)).scalar()
        if q_result:
            nrofaccounts = q_result

        q_result = db.session.query(db.func.max(AccountStat.updated_at)).scalar()
        if q_result:
            lastupdate = q_result

        q_result = db.session.query(db.func.max(AccountStat.lastepochmined)).scalar()
        if q_result:
            lastepochmined = q_result
            prev_epoch = lastepochmined - 1

        q_result = db.engine.execute(f"select avg(proofssubmitted) as average from minerhistory where epoch = {prev_epoch}").scalar()
        if q_result:
            avg_proofs_mined_last_epoch = round(q_result, 2)

        q_result = db.engine.execute("select sum(pe.amount) from paymentevent pe join (select address, max(height) as height from paymentevent group by address) pe2 on pe.address = pe2.address and pe.height = pe2.height").scalar()
        if q_result:
            rewards_last_epoch = round(q_result / 1000, 2)

        q_result = db.engine.execute(f"select sum(proofssubmitted) as proofs from minerhistory where epoch = {prev_epoch}").scalar()
        if q_result:
            proofs_submitted_last_epoch = q_result

        if rewards_last_epoch and proofs_submitted_last_epoch:
            reward_pp_last_epoch = round(float(rewards_last_epoch) / float(proofs_submitted_last_epoch), 3)

        q_result = db.engine.execute(f"select address, epoch, proofssubmitted from minerhistory where epoch > {prev_epoch} - 10 order by 1, 2 asc").all()
        if q_result:
            miner_history = q_result

        chart_data = {}
        for address, epoch, proofs in miner_history:
            if address in chart_data:
                chart_data[address]["labels"].append(epoch)
                chart_data[address]["values"].append(proofs)
            else:
                data_dict = {"labels": [], "values": []}
                data_dict["labels"].append(epoch)
                data_dict["values"].append(proofs)
                chart_data[address] = data_dict
    except Exception as e:
        print(f"{e}")

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
                           address_url=address_url,
                           chart_data=chart_data,
                           proofs_submitted_last_epoch=proofs_submitted_last_epoch,
                           reward_pp_last_epoch=reward_pp_last_epoch)

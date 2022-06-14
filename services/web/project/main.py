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
    chart_epoch = {}
    chart_reward = {}
    chart_overall_perf = {"labels": [], "proofs": [], "amount": [], "amountpp": [], "nrofaccounts": []}
    prev_epoch = 0
    miner_history = {}
    payment_events = {}

    try:
        rows = AccountStat.query.order_by(db.asc(AccountStat.name)).all()

        q_result = db.session.query(db.func.sum(AccountStat.balance)).scalar()
        if q_result:
            totalbalance = round((q_result / 1000), 2)

        q_result = db.session.query(db.func.sum(AccountStat.towerheight)).scalar()
        if q_result:
            totalheight = q_result

        q_result = db.engine.execute("select count(*) from accountstat where lastepochmined in (select max(lastepochmined) from accountstat)").scalar()
        if q_result:
            miners = q_result

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
            reward_pp_last_epoch = round(float(rewards_last_epoch) / float(proofs_submitted_last_epoch), 2)

        q_result = db.engine.execute(f"select address, epoch, proofssubmitted from minerhistory where epoch > {prev_epoch} - 10 order by 1, 2 asc").all()
        if q_result:
            miner_history = q_result

        for address, epoch, proofs in miner_history:
            if address in chart_epoch:
                chart_epoch[address]["labels"].append(epoch)
                chart_epoch[address]["values"].append(proofs)
            else:
                data_dict = {"labels": [], "values": []}
                data_dict["labels"].append(epoch)
                data_dict["values"].append(proofs)
                chart_epoch[address] = data_dict

        q_result = db.engine.execute("select address, amount / 1000 as amount, ranknr from (select address, amount, rank() over (partition by address order by address, height desc) ranknr from paymentevent) pe where ranknr <= 10 order by 1, 3 desc").all()
        if q_result:
            payment_events = q_result

        for address, amount, ranknr in payment_events:
            if address in chart_reward:
                chart_reward[address]["labels"].append(prev_epoch + 1 - ranknr)
                chart_reward[address]["values"].append(amount)
            else:
                data_dict = {"labels": [], "values": []}
                data_dict["labels"].append(prev_epoch + 1 - ranknr)
                data_dict["values"].append(amount)
                chart_reward[address] = data_dict

        q_result = db.engine.execute("select mh.ranknr, mh.epoch, sum(proofssubmitted) as proofssubmitted, sum(amount) as amount, sum(amount) / sum(proofssubmitted) as amountpp, count(*) as nrofaccounts from (select address, epoch, proofssubmitted, rank() over (partition by address order by address, epoch desc) ranknr from minerhistory) mh join (select address, amount, rank() over (partition by address order by address, height desc) ranknr from paymentevent) pe on mh.address = pe.address and mh.ranknr = pe.ranknr where mh.ranknr <= 30 group by mh.epoch, mh.ranknr order by epoch").all()
        if q_result:
            overal_perf_data = q_result

        for ranknr, epoch, proofssubmitted, amount, amountpp, acccount in overal_perf_data:
            chart_overall_perf["labels"].append(epoch)
            chart_overall_perf["proofs"].append(proofssubmitted)
            chart_overall_perf["amount"].append(amount / 1000)
            chart_overall_perf["amountpp"].append(amountpp / 1000)
            chart_overall_perf["nrofaccounts"].append(acccount)

    except Exception as e:
        print(f"{e}")

    return render_template('dashboard.html',
                           name=current_user.name,
                           rows=rows,
                           totalbalance=int(totalbalance),
                           totalheight=totalheight,
                           lastupdate=lastupdate,
                           miners=miners,
                           lastepochmined=lastepochmined,
                           avg_proofs_mined_last_epoch=avg_proofs_mined_last_epoch,
                           rewards_last_epoch=rewards_last_epoch,
                           address_url=address_url,
                           chart_epoch=chart_epoch,
                           chart_reward=chart_reward,
                           proofs_submitted_last_epoch=proofs_submitted_last_epoch,
                           reward_pp_last_epoch=reward_pp_last_epoch,
                           chart_overall_perf=chart_overall_perf)

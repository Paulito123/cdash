from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountStat, MinerHistory, PaymentEvent, NetworkStat, Epoch
from .config import Config
from . import db
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        name = current_user.name
    else:
        name = ""
    return render_template('index.html', name=name)


@main.route('/miners')
@login_required
def miners():
    address_url = Config.BASE_URL + "address/"
    rows = []
    totalbalance = 0
    totalheight = 0
    lastupdate = 0
    currentepoch = 0
    miners = 0
    avg_proofs_mined_last_epoch = 0
    rewards_last_epoch = 0
    proofs_submitted_last_epoch = 0
    reward_pp_last_epoch = 0
    chart_epoch = {}
    chart_reward = {} # , , ,
    chart_overall_perf = {"labels": [], "proofs": [], "amount": [], "amountpp": [], "nrofaccounts": []}
    overal_perf_data = []
    prev_epoch = 0
    miner_history = {}
    payment_events = {}

    try:
        rows = AccountStat.query.order_by(db.asc(AccountStat.name)).all()

        q_result = db.session.query(db.func.sum(AccountStat.balance)).scalar()
        if q_result:
            totalbalance = int((q_result / 1000))

        q_result = db.session.query(db.func.sum(AccountStat.towerheight)).scalar()
        if q_result:
            totalheight = q_result

        q_result = db.session.query(db.func.max(NetworkStat.epoch)).scalar()
        if q_result:
            currentepoch = q_result
            prev_epoch = currentepoch - 1

        q_result = db.engine.execute(f"select count(*) from accountstat where lastepochmined = {currentepoch}").scalar()
        if q_result:
            miners = q_result

        q_result = db.session.query(db.func.max(AccountStat.updated_at)).scalar()
        if q_result:
            lastupdate = q_result

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

        q_result = db.engine.execute("with epochs as (select epoch, height, COALESCE(lag(height, 1) over (order by epoch desc), 9999999999) as pheight from epoch e join (select max(epoch) - 30 cutoff from epoch) e2 on e.epoch >= e2.cutoff), payments as (select height, sum(amount) as amount, count(distinct address) as nrofaccounts from paymentevent group by height), proofs as (select e.epoch, e.height, e.pheight, coalesce(sum(m.proofssubmitted), 0) as proofssubmitted from epochs e left join minerhistory m on m.epoch = e.epoch group by e.epoch, height, pheight), joined as (select pr.epoch, pr.proofssubmitted, sum(p.amount) as amount, sum(nrofaccounts) as nrofaccounts from proofs pr left join payments p on p.height >= pr.height and p.height < pr.pheight group by pr.epoch, pr.proofssubmitted), corrected as (select epoch, proofssubmitted, coalesce(lag(amount, 1) over (order by epoch desc), 0) as amount, coalesce(lag(nrofaccounts, 1) over (order by epoch desc), 0) as nrofaccounts from joined) select epoch, proofssubmitted, amount, nrofaccounts from corrected where epoch < (select max(epoch) from epoch) order by 1").all()
        if q_result:
            overal_perf_data = q_result

        for epoch, proofssubmitted, amount, nrofaccounts in overal_perf_data:
            chart_overall_perf["labels"].append(epoch)
            chart_overall_perf["proofs"].append(proofssubmitted)
            chart_overall_perf["amount"].append(int(amount/1000))
            chart_overall_perf["amountpp"].append(float((amount / proofssubmitted if proofssubmitted > 0 else 1) / 1000))
            chart_overall_perf["nrofaccounts"].append(int(nrofaccounts))

    except Exception as e:
        print(f"{e}")

    return render_template('miners.html',
                           name=current_user.name,
                           rows=rows,
                           totalbalance=totalbalance,
                           totalheight=totalheight,
                           lastupdate=lastupdate,
                           miners=miners,
                           currentepoch=currentepoch,
                           avg_proofs_mined_last_epoch=avg_proofs_mined_last_epoch,
                           rewards_last_epoch=rewards_last_epoch,
                           address_url=address_url,
                           chart_epoch=chart_epoch,
                           chart_reward=chart_reward,
                           proofs_submitted_last_epoch=proofs_submitted_last_epoch,
                           reward_pp_last_epoch=reward_pp_last_epoch,
                           chart_overall_perf=chart_overall_perf)


@main.route('/network')
@login_required
def network():
    netstats = []
    chart_epoch = {"epoch": [], "height": [], "proofs": [], "minerpaymenttotal": [], "miners": [], "minerspayable": [], "minerspayableproofs": [], "timestamp": [], "validatorproofs": [], "updated_at": []}

    try:
        netstats = db.session.query(
            NetworkStat.epoch,
            NetworkStat.height,
            NetworkStat.progress,
            NetworkStat.activeminers,
            NetworkStat.totaladdresses,
            NetworkStat.totalminers,
            NetworkStat.totalsupply,
            NetworkStat.updated_at).first()

        cutoff = int(netstats['epoch']) - 60

        epochs = db.session.query(
            Epoch.epoch,
            Epoch.height,
            Epoch.proofs,
            Epoch.minerpaymenttotal,
            Epoch.miners,
            Epoch.minerspayable,
            Epoch.minerspayableproofs,
            Epoch.timestamp,
            Epoch.validatorproofs,
            Epoch.updated_at).filter(Epoch.epoch >= cutoff).order_by(Epoch.epoch).all()

        for epoch, height, proofs, minerpaymenttotal, miners, minerspayable, minerspayableproofs, timestamp, validatorproofs, updated_at in epochs:
            chart_epoch["epoch"].append(epoch)
            chart_epoch["height"].append(height)
            proofs_safe = proofs if proofs else 0
            chart_epoch["proofs"].append(proofs_safe)
            minerpaymenttotal_safe = minerpaymenttotal if minerpaymenttotal else 0
            chart_epoch["minerpaymenttotal"].append(minerpaymenttotal_safe)
            miners_safe = miners if miners else 0
            chart_epoch["miners"].append(miners_safe)
            minerspayable_safe = minerspayable if minerspayable else 0
            chart_epoch["minerspayable"].append(minerspayable_safe)
            minerspayableproofs_safe = minerspayableproofs if minerspayableproofs else 0
            chart_epoch["minerspayableproofs"].append(minerspayableproofs_safe)
            timestamp_safe = timestamp.strftime("%m/%d/%Y, %H:%M:%S") if timestamp else '0'
            chart_epoch["timestamp"].append(timestamp_safe)
            validatorproofs_safe = validatorproofs if validatorproofs else '0'
            chart_epoch["validatorproofs"].append(validatorproofs_safe)
            chart_epoch["updated_at"].append(updated_at.strftime("%m/%d/%Y, %H:%M:%S"))

    except Exception as e:
        print(f"[{datetime.now()}]:[ERROR]:{e}")

    return render_template('network.html',
                           name=current_user.name,
                           netstats=netstats,
                           chart_epoch=chart_epoch)

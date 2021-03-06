from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountStat, NetworkStat, Epoch
from .config import Config
from . import db
from datetime import datetime


main = Blueprint('main', __name__)
sess_timeout_secs = (Config.SESS_TIMEOUT_MINS * 60) + 5


@main.route('/')
def index():
    if current_user.is_authenticated:
        name = current_user.name
    else:
        name = ""
    return render_template('index.html', name=name, sess_timeout=sess_timeout_secs)


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
    chart_reward = {}
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

        q_result = db.engine.execute(f"select rewards from vw_epoch_rich where epoch = {prev_epoch}").scalar()
        if q_result:
            rewards_last_epoch = round(q_result, 2)

        q_result = db.engine.execute(f"select proofs from vw_epoch_rich where epoch = {prev_epoch}").scalar()
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

        q_result = db.engine.execute("select k.epoch, p.address, sum(p.amount) as amount from paymentevent p left join vw_epoch_keys k on p.height >= k.height and p.height < k.pheight where k.epoch >= (select max(epoch) - 10 from vw_epoch_keys) group by k.epoch, p.address order by 2, 1").all()
        if q_result:
            payment_events = q_result

        for epoch, address, amount in payment_events:
            if address in chart_reward:
                chart_reward[address]["labels"].append(epoch - 1)
                chart_reward[address]["values"].append(amount)
            else:
                data_dict = {"labels": [], "values": []}
                data_dict["labels"].append(epoch - 1)
                data_dict["values"].append(amount)
                chart_reward[address] = data_dict

        q_result = db.engine.execute(f"select epoch, proofs, rewards, accounts from vw_epoch_rich where epoch >= {prev_epoch} - {Config.CHART_EPOCHS_MINERS} and epoch < (select max(epoch) from epoch) order by 1").all()
        if q_result:
            overal_perf_data = q_result

        for epoch, proofssubmitted, amount, nrofaccounts in overal_perf_data:
            chart_overall_perf["labels"].append(epoch)
            chart_overall_perf["proofs"].append(proofssubmitted)
            chart_overall_perf["amount"].append(int(amount))
            chart_overall_perf["amountpp"].append(float((amount / proofssubmitted if proofssubmitted > 0 else 1)))
            chart_overall_perf["nrofaccounts"].append(int(nrofaccounts))

    except Exception as e:
        print(f"{e}")

    return render_template('miners.html',
                           sess_timeout=sess_timeout_secs,
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
    netstats = {}
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

        if netstats:

            cutoff = int(netstats['epoch']) - Config.CHART_EPOCHS_NETWORK

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
                minerpaymenttotal_safe = round(minerpaymenttotal if minerpaymenttotal else 0, 0)
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
        else:
            # Default value when data is not yet available
            netstats = {"epoch": 0, "height": 0, "progress": 0.0, "activeminers": 0, "totaladdresses": 0, "totalminers": 0, "totalsupply": 0, "updated_at": datetime. strptime("1900-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')}

    except Exception as e:
        print(f"[{datetime.now()}]:[ERROR]:{e}")

    return render_template('network.html',
                           sess_timeout=sess_timeout_secs,
                           name=current_user.name,
                           netstats=netstats,
                           chart_epoch=chart_epoch)

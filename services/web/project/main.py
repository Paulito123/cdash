from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountStat
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
    return render_template('dashboard.html',
                           name=current_user.name,
                           rows=rows,
                           totalbalance=totalbalance,
                           totalheight=totalheight,
                           lastupdate=lastupdate,
                           nrofaccounts=nrofaccounts,
                           lastepochmined=lastepochmined)

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import AccountMetric
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    rows = AccountMetric.query.all()
    som = db.session.query(db.func.sum(AccountMetric.balance)).scalar()
    return render_template('dashboard.html', name=current_user.name, rows=rows, som=som)

from datetime import datetime
from random import getrandbits
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from pyotp import HOTP, TOTP
from . import db
from .models import User
from .config import Config

auth = Blueprint('auth', __name__)
sess_timeout_secs = (Config.SESS_TIMEOUT_MINS * 60) + 5


@auth.route('/login')
def login():
    return render_template('login.html', sess_timeout=sess_timeout_secs)


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    nu = datetime.now()

    if not user:
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    elif user.wronglogins >= Config.MAX_OTP_ATTEMPTS \
            and (nu - user.updated_at).total_seconds() < Config.TIMEOUT_AFTER_FAILED_LOGINS:
        flash('Too many wrong login attempts!')
        return redirect(url_for('auth.login'))
    elif not user.check_password(password=password):
        if user.wronglogins >= Config.MAX_OTP_ATTEMPTS:
            user.wronglogins = 1
        else:
            user.wronglogins = user.wronglogins + 1
        db.session.add(user)
        db.session.commit()
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    else:
        # if the above checks pass, then we know the user has the right credentials
        user.wronglogins = 0
        db.session.add(user)
        db.session.commit()

        session['remember'] = remember
        session['email'] = email
        return redirect(url_for('auth.otp'))


@auth.route('/otp')
def otp():
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('auth.login'))
    elif current_user.is_authenticated:
        return redirect(url_for('main.miners'))
    return render_template('otp.html', sess_timeout=sess_timeout_secs)


@auth.route('/otp', methods=['POST'])
def otp_post():
    email = session.get('email')
    remember = session.get('remember')
    user = User.query.filter_by(email=email).first()

    if not user:
        session.pop('email', default=None)
        session.pop('remember', default=None)
        flash('Please provide login details first.')
        return redirect(url_for('auth.login'))

    otp_input = request.form.get('otp')
    totp = TOTP(user.totp)
    totp_now = totp.now()

    nu = datetime.now()

    if user.wronglogins >= Config.MAX_OTP_ATTEMPTS \
            and (nu - user.updated_at).total_seconds() < Config.TIMEOUT_AFTER_FAILED_LOGINS:
        session.pop('email', default=None)
        session.pop('remember', default=None)
        flash('Too many wrong login attempts!')
        return redirect(url_for('auth.login'))
    elif otp_input == totp_now:
        user.wronglogins = 0
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=remember)
        return redirect(url_for('main.miners'))
    else:
        user.wronglogins = user.wronglogins + 1
        db.session.add(user)
        db.session.commit()
        flash('OTP incorrect, please try again.')
        return redirect(url_for('auth.otp'))


@auth.route('/logout')
@login_required
def logout():
    session['id'] = None
    session['remember'] = None
    logout_user()
    return redirect(url_for('main.index'))

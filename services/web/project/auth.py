from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from pyotp import HOTP, TOTP
from .models import User
from .config import Config

auth = Blueprint('auth', __name__)
sess_timeout_secs = (Config.SESS_TIMEOUT * 60) + 5


@auth.route('/login')
def login():
    return render_template('login.html', sess_timeout=sess_timeout_secs)


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not user.check_password(password=password):
        flash('Please check your login details and try again.')
        # if user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    session['id'] = user.id
    session['remember'] = remember
    return redirect(url_for('auth.otp'))


@auth.route('/otp')
def otp():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))
    elif current_user.is_authenticated:
        return redirect(url_for('main.miners'))
    return render_template('otp.html', sess_timeout=sess_timeout_secs)


@auth.route('/otp', methods=['POST'])
def otp_post():
    user_id = session.get('id')
    remember = session.get('remember')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        session['id'] = None
        session['remember'] = None
        return redirect(url_for('auth.login'))

    otp_input = request.form.get('otp')
    totp = TOTP(user.totp)
    totp_now = totp.now()

    if otp_input == totp_now:
        login_user(user, remember=remember)
        return redirect(url_for('main.miners'))
    else:
        flash('OTP incorrect, please retry.')
        return redirect(url_for('auth.otp'))


@auth.route('/logout')
@login_required
def logout():
    session['id'] = None
    session['remember'] = None
    logout_user()
    return redirect(url_for('main.index'))

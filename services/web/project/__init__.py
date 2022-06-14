from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pytz import timezone, utc

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object("project.config.Config")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    @app.template_filter('to_cet')
    def datetimefilter(value):
        """Converts a given UTC datetime into CET datetime"""
        format = "%Y-%m-%d %H:%M:%S"
        tz = timezone('Europe/Brussels')
        u = timezone('UTC')
        value = u.localize(value, is_dst=None).astimezone(utc)
        local_dt = value.astimezone(tz)
        return local_dt.strftime(format)

    @app.template_filter('sep_int')
    def sep_int(value):
        """Applies thousands separator to numeric values"""
        return '{:,}'.format(int(value))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

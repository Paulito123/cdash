import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    SECRET_KEY = f"{os.getenv('SECRET_KEY')}"
    BASE_URL = f"{os.getenv('BASE_URL')}"
    CHART_EPOCHS_MINERS = 60
    CHART_EPOCHS_NETWORK = 60
    SESS_TIMEOUT_MINS = int(os.getenv('SESS_TIMEOUT_MINS'))
    REDIS_URI = os.getenv("SESSION_REDIS")
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(REDIS_URI)
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = int(os.getenv('SESS_TIMEOUT_MINS')) * 60
    MAX_LOGIN_ATTEMPTS = 5
    MAX_OTP_ATTEMPTS = 5
    TIMEOUT_AFTER_FAILED_LOGINS = 300

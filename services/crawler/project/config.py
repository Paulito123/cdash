import os


class Config(object):
    SLEEP_MINS = 15
    BASE_URL = f"{os.getenv('BASE_URL')}"

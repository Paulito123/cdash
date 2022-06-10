import os


class Config(object):
    SLEEP_MINS = f"{os.getenv('SLEEP_MINS')}"
    BASE_URL = f"{os.getenv('BASE_URL')}"
    INITIAL_SLEEP_SECS = f"{os.getenv('INITIAL_SLEEP_SECS')}"

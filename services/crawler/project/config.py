import os


class Config(object):
    SLEEP_MINS = f"{os.getenv('SLEEP_MINS')}"
    BASE_URL = f"{os.getenv('BASE_URL')}"
    INITIAL_SLEEP_SECS = f"{os.getenv('INITIAL_SLEEP_SECS')}"
    BOT_TOKEN = f"{os.getenv('BOT_TOKEN')}"
    CHAT_ID = f"{os.getenv('CHAT_ID')}"
    ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM')

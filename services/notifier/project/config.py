import os


class Config(object):
    BOT_TOKEN = f"{os.getenv('BOT_TOKEN')}"
    CHAT_ID = f"{os.getenv('CHAT_ID')}"
    ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM')

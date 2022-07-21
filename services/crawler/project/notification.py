# import os
# import json
from datetime import datetime
# from helper import convert_timezone
from database import session, engine
# from models import EventLog
# from agents import Emoji, Telegram
# from config import Config


def health_check():
    nu = datetime.now()
    epoch = engine.execute("select max(created_at) from eventlog where left(type, 23) = 'Notif application error'").one()

    print(f"nu={nu} | epoch={epoch[0]}")

    # notifier = Telegram(Config.BOT_TOKEN, Config.CHAT_ID)
    # resp = notifier.send_message("notification").json()

    # if resp['ok']:
    #     print("True")
    # else:
    #     print("False")

    # type = "Notif application error success" if True else "Notif application error failed"
    # print(type)


if __name__ == "__main__":
    health_check()

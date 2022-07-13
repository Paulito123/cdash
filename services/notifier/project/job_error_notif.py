#!/usr/local/bin/python
import os
import json
from datetime import datetime
from helper import convert_timezone
from database import session, engine
from models import EventLog
from agents import Emoji, Telegram
from config import Config


if Config.ENABLE_TELEGRAM == "1":
    try:
        delay = Config.ERROR_NOTIF_DELAY
        notifier = Telegram(Config.BOT_TOKEN, Config.CHAT_ID)

        # # Application errors alerts
        # send_message = engine.execute(f"select case when max(created_at) > (NOW() - interval '{delay} hour')::timestamp then 0 else 1 end as notif_flag from eventlog where left(type, 23) = 'Notif application error'").scalar()
        # # send_message = engine.execute(f"select case when max(created_at) > (NOW() - interval '5 minutes')::timestamp then 0 else 1 end as notif_flag from eventlog where left(type, 23) = 'Notif application error'").scalar()
        #
        # if send_message == 1:
        #     error_count = engine.execute("select count(*) from eventlog where left(type, 17) = 'Application error' and created_at > (select coalesce(max(created_at), '2022-01-01 00:00:00.00000') from eventlog where left(type, 23) = 'Notif application error')").scalar()
        #     if int(error_count) > 0:
        #         notification = f"{Emoji.print(Emoji, emoji_name='cross_red')}[APPLICATION ERROR ALERT]\n" \
        #                        "\n" \
        #                        f"A total of [{error_count}] application errors have been recorded since the last error notification!\n"
        #
        #         resp = notifier.send_message(notification).json()
        #         type = f"Notif application error {'success' if resp['ok'] else 'failed'}"
        #         jobname = os.path.basename(__file__)
        #
        #         o = EventLog(event_source=jobname, type=type, message=notification, response=resp)
        #         session.add(o)
        #         session.commit()

        # Miner inactivity alerts
        send_message = engine.execute(f"select case when max(created_at) > (NOW() - interval '{delay} hour')::timestamp then 0 else 1 end as notif_flag from eventlog where left(type, 21) = 'Notif miners inactive'").scalar()

        if send_message == 1:
            error_count = engine.execute("with maxts as (select address, max(timestamp) as mts from chainevent group by address) select count(*) from maxts m join accountstat a on m.address = a.address where mts < (NOW() - interval '2 hour')::timestamp and proofsinepoch < 72").scalar()
            if int(error_count) > 0:
                notification = f"{Emoji.print(Emoji, emoji_name='heavy_exclamation')}[MINERS INACTIVE WARNING]\n" \
                               "\n" \
                               f"A total of [{error_count}] miners are not submitting proof in a timely fashion since last notification!\n"

                resp = notifier.send_message(notification).json()
                type = f"Notif miners inactive {'success' if resp['ok'] else 'failed'}"
                jobname = os.path.basename(__file__)

                o = EventLog(event_source=jobname, type=type, message=notification, response=resp)
                session.add(o)
                session.commit()

    except Exception as e:
        print(f"[{datetime.now()}]:[ERROR]:{e}")

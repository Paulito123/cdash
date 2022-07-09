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
        epoch = engine.execute("select epoch, round(rewards / 1000, 0) from vw_epoch_rich where epoch = (select max(epoch) - 1 from networkstat)").one()
        balance = engine.execute("select sum(balance)/1000 from accountstat").scalar()
        balance_multiplier = int(int(balance) / 100000)
        acc_stat_info = engine.execute("select count(a.*), max(a.updated_at), max(b.addresses) from accountstat a cross join (select count(distinct address) as addresses from accountstat) b where a.lastepochmined = (select max(epoch) from networkstat)").one()
        netw_stat_info = engine.execute("select epoch, totalsupply, activeminers from networkstat where id = 1").one()

        notifier = Telegram(Config.BOT_TOKEN, Config.CHAT_ID)
        notification = f"{Emoji.print(Emoji, emoji_name='check')}[DAILY UPDATE]{Emoji.print(Emoji, emoji_name='chart')}\n" \
                       "\n" \
                       f"[TOTAL BALANCE]{Emoji.print(Emoji, emoji_name='money_bag') * balance_multiplier}\n" \
                       f"{'{:,}'.format(int(balance))}\n" \
                       "\n" \
                       f"[NETWORK STATUS]{Emoji.print(Emoji, emoji_name='lightning')}\n" \
                       f"Epoch: {'{:,}'.format(int(netw_stat_info[0]))}\n" \
                       f"Total supply: {'{:,}'.format(int(netw_stat_info[1]))}\n" \
                       f"Active miners: {'{:,}'.format(int(netw_stat_info[2]))}\n" \
                       "\n" \
                       f"[MINER STATUS EPOCH {epoch[0]}]{Emoji.print(Emoji, emoji_name='builder')}\n" \
                       f"Rewards received E-1: {'{:,}'.format(int(epoch[1]))}\n" \
                       f"Active miners: {acc_stat_info[0]}/{acc_stat_info[2]}\n" \
                       f"Last data update: {convert_timezone(acc_stat_info[1])[:19]}\n"

        resp = notifier.send_message(notification).json()
        type = "Notif daily status success" if resp['ok'] == "True" else "Notif daily status failed"
        jobname = os.path.basename(__file__)

        o = EventLog(event_source=jobname, type=type, message=notification, response=f"{resp}")
        session.add(o)
        session.commit()

    except Exception as e:
        print(f"[{datetime.now()}]:[ERROR]:{e}")

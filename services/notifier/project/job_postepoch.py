#!/usr/local/bin/python
import os
import json
from datetime import datetime
from helper import convert_timezone
from database import session, engine
from models import CronLog
from agents import Emoji, Telegram
from config import Config


if Config.ENABLE_TELEGRAM == "1":
    epoch = engine.execute("select epoch, round(rewards / 1000, 0) from vw_epoch_rich where epoch = (select max(epoch) - 1 from networkstat)").one()
    acc_stat_info = engine.execute("select count(a.*), max(a.updated_at), max(b.addresses) from accountstat a cross join (select count(distinct address) as addresses from accountstat) b where a.lastepochmined = (select max(epoch) from networkstat)").one()
    netw_stat_info = engine.execute("select epoch, totalsupply, activeminers from networkstat where id = 1").one()

    notifier = Telegram(Config.BOT_TOKEN, Config.CHAT_ID)
    notification = f"{Emoji.print(Emoji, emoji_name='check')}[DAILY UPDATE]{Emoji.print(Emoji, emoji_name='chart')*3}\n" \
                   "\n" \
                   f"[NETWORK STATUS]{Emoji.print(Emoji, emoji_name='lightning')*3}\n" \
                   f"Epoch: [{'{:,}'.format(int(netw_stat_info[0]))}]\n" \
                   f"Total supply: [{'{:,}'.format(int(netw_stat_info[1]))}]\n" \
                   f"Active miners: [{'{:,}'.format(int(netw_stat_info[2]))}]\n" \
                   "\n" \
                   f"[MINER STATUS EPOCH {epoch[0]}]{Emoji.print(Emoji, emoji_name='money_bag')*3}\n" \
                   f"Rewards received: [{'{:,}'.format(int(epoch[1]))}]\n" \
                   f"Active miners: [{acc_stat_info[0]}/{acc_stat_info[2]}]\n" \
                   f"Last data update: [{convert_timezone(acc_stat_info[1])[:19]}]\n"

    resp = notifier.send_message(notification).json()
    status = "OK" if resp['ok'] == "True" else "ERROR"
    jobname = os.path.basename(__file__)

    o = CronLog(jobname=jobname, status=status, response=f"{resp}")
    session.add(o)
    session.commit()

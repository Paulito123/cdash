import requests
from lxml import html
from time import sleep
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from models import AccountStat
from database import session, engine
from config import Config
from datetime import datetime


def get_source(page_url):
    """
    A function to download the page source of the given URL.
    """
    r = requests.get(page_url)
    source = html.fromstring(r.content)

    return source


def scrape():
    with engine.connect() as connection:
        try:
            accounts = connection.execute(text("select address from accountstat"))

            for account in accounts:
                www_page = Config.BASE_URL + 'address/' + account.address
                source = get_source(www_page)

                address = source.xpath("//span[contains(@class, 'address_addressText__YS_A5')]/text()")
                balance = source.xpath("//span[contains(@class, 'address_balanceText__ds0io')]/text()")
                height = source.xpath(
                    "//div[contains(@class, 'address_proofHistoryTable__oSdpQ')]/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[2]/text()")
                proofsinepoch = source.xpath(
                    "//div[contains(@class, 'address_proofHistoryTable__oSdpQ')]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td[2]/text()")
                lastepochmined = source.xpath(
                    "//div[contains(@class, 'address_proofHistoryTable__oSdpQ')]/div[2]/div/div/div/div/div/table/tbody/tr[3]/td[2]/text()")

                if len(address) > 0:
                    sess_account = session.query(AccountStat).filter_by(address=account.address).first()

                    if sess_account:
                        if len(balance) > 0:
                            sess_account.balance = int(round(float(balance[0].replace(',', '')), 3) * 1000)
                            sess_account.updated_at = datetime.now()

                        if len(height) > 0:
                            sess_account.towerheight = int(height[0])

                        if len(proofsinepoch) > 0:
                            sess_account.proofsinepoch = int(proofsinepoch[0])

                        if len(lastepochmined) > 0:
                            sess_account.lastepochmined = int(lastepochmined[0])

                        if len(height) > 0 or len(balance) > 0 or len(proofsinepoch) > 0 or len(lastepochmined) > 0:
                            sess_account.updated_at = datetime.now()
                            session.commit()
        except ProgrammingError:
            print("Try init DB!")

if __name__ == "__main__":
    while True:
        sleep(60)
        scrape()
        sleep(60 * Config.SLEEP_MINS)

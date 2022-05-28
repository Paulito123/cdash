import requests
from lxml import html
from time import sleep
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from models import AccountMetric
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
            accounts = connection.execute(text("select address from accountmetric"))

            for account in accounts:
                www_page = Config.BASE_URL + 'address/' + account.address
                source = get_source(www_page)

                address = source.xpath("//span[contains(@class, 'address_addressText__YS_A5')]/text()")
                balance = source.xpath("//span[contains(@class, 'address_balanceText__ds0io')]/text()")
                height = source.xpath(
                    "//div[contains(@class, 'address_proofHistoryTable__oSdpQ')]/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[2]/text()")

                if len(address) > 0:
                    sess_account = session.query(AccountMetric).filter_by(address=account.address).first()

                    if sess_account:
                        if len(balance) > 0:
                            sess_account.balance = int(round(float(balance[0].replace(',', '')), 2) * 100)
                            sess_account.updated_at = datetime.now()

                        if len(height) > 0:
                            sess_account.towerheight = int(height[0])
                            sess_account.updated_at = datetime.now()

                        if len(height) > 0 or len(balance) > 0:
                            session.commit()
        except ProgrammingError:
            print("Try init DB!")


while True:
    sleep(60)
    scrape()
    sleep(60 * Config.SLEEP_MINS)

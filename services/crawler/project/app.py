import requests
from time import sleep
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from models import AccountStat
from database import session, engine
from config import Config
from datetime import datetime


def fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list):
    print("Waiting for data...")
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_button_next))

    # Crawling miner history
    disabled = False
    while not disabled:

        rows = driver.find_elements(By.XPATH, xp_rows)
        for row in rows:
            if len(row.find_elements(By.TAG_NAME, "td")[0].text) == 0:
                print("skip empty")
                continue

            col_index = 0
            for data_name in data_name_list:
                v = row.find_elements(By.TAG_NAME, "td")[col_index]
                print(f"{data_name} = {v.text}")
                col_index = col_index + 1

        button_next = driver.find_element(By.XPATH, xp_button_next)
        disabled = button_next.get_property('disabled')
        button_next.click()


def scrape():
    with engine.connect() as connection:
        try:
            # Fetch the account list
            accounts = connection.execute(text("select address from accountstat"))

            # iterate account list
            for account in accounts:
                url = Config.BASE_URL + 'address/' + account.address
                exec_host = 'chrome'

                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("start-maximized")
                chrome_options.add_argument("disable-infobars")
                chrome_options.add_argument("--disable-extensions")

                driver = webdriver.Remote(
                    command_executor=f'http://{exec_host}:4444/wd/hub',
                    options=chrome_options
                )

                try:
                    driver.get(url)

                    address = driver.find_element(By.CLASS_NAME, "address_addressText__YS_A5")
                    balance = driver.find_element(By.CLASS_NAME, "address_balanceText__ds0io")
                    height = driver.find_element(By.XPATH,
                                                 "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[2]")
                    proofsinepoch = driver.find_element(By.XPATH,
                                                        "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td[2]")
                    lastepochmined = driver.find_element(By.XPATH,
                                                         "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[3]/td[2]")

                    xp_rows = "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr"
                    xp_button_next = "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[2]/div[2]/div/div/ul/li[@title='Next Page']/button"
                    data_name_list = ["Epoch", "Proofs submitted"]
                    fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list)

                    xp_rows = "//div[contains(@class, 'eventsTable_inner__HsGHV')]/div[2]/div/div/div/div/div/table/tbody/tr"
                    xp_button_next = "//div[contains(@class, 'eventsTable_inner__HsGHV')]/div[2]/div/div/ul/li[@title='Next Page']/button"
                    data_name_list = ["height", "type", "amount", "sender", "recipient"]
                    fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list)
                except Exception as e:
                    print(f"{e}")
                finally:
                    driver.quit()


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

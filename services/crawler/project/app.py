import requests
from time import sleep
from sqlalchemy import text, func
from sqlalchemy.exc import ProgrammingError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from models import AccountStat, MinerHistory, PaymentEvent
from database import session, engine
from config import Config
from datetime import datetime


def fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list, last_known_kv) -> []:
    """
    :param driver: selenium driver
    :param xp_rows: xpath to tr element of the data table
    :param xp_button_next: xpath to the next button
    :param data_name_list: column names of data table
    :param last_known_kv: column name and value of last known record
    :return: list of dictionaries
    """
    output_list = []

    # last known key value pair
    if len(last_known_kv) > 0:
        lkk = last_known_kv[0]
        lkv = last_known_kv[1]
    else:
        lkk = ""
        lkv = 0

    # Wait for the page to load
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_button_next))

    # var used to keep track of when next button is disabled
    disabled = False
    break_flag = False

    # Crawling table data
    while not disabled:
        # get table rows by xpath
        rows = driver.find_elements(By.XPATH, xp_rows)

        # iterate data row by row
        for row in rows:
            # discard empty rows
            if len(row.find_elements(By.TAG_NAME, "td")[0].text) == 0:
                continue

            # iterate columns
            col_index = 0
            output_dict = {}
            for data_name in data_name_list:
                v = row.find_elements(By.TAG_NAME, "td")[col_index]

                # check if record already exists
                if len(lkk) > 0 and data_name == lkk and v.text == lkv:
                    # set break flag because record already exists in DB
                    break_flag = True
                    break

                output_dict[f"{data_name}"] = f"{v.text}"
                col_index = col_index + 1

            if break_flag:
                # break out row iteration
                break
            else:
                # append the row dict to output list
                output_list.append(output_dict)

        if break_flag:
            # break out of while
            break

        # click and check status of the next button to determine if all data is loaded
        button_next = driver.find_element(By.XPATH, xp_button_next)
        disabled = button_next.get_property('disabled')
        button_next.click()

    return output_list


def scrape():
    exec_host = 'chrome'
    with engine.connect() as connection:
        try:
            # Fetch the account list
            accounts = connection.execute(text("select address from accountstat"))

            # iterate account list
            for account in accounts:
                url = Config.BASE_URL + 'address/' + account.address

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

                    # fetch tower stats
                    address = driver.find_element(By.CLASS_NAME, "address_addressText__YS_A5")
                    balance = driver.find_element(By.CLASS_NAME, "address_balanceText__ds0io")
                    height = driver.find_element(By.XPATH,
                                                 "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[2]")
                    proofsinepoch = driver.find_element(By.XPATH,
                                                        "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td[2]")
                    lastepochmined = driver.find_element(By.XPATH,
                                                         "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[1]/div[2]/div/div/div/div/div/table/tbody/tr[3]/td[2]")

                    # write tower stats to DB
                    sess_account = session.query(AccountStat).filter_by(address=address.text).first()
                    if sess_account:
                        if len(balance.text) > 0:
                            sess_account.balance = int(round(float(balance.text.replace(',', '')), 3) * 1000)
                            sess_account.updated_at = datetime.now()

                        if len(height.text) > 0:
                            sess_account.towerheight = int(height.text)

                        if len(proofsinepoch.text) > 0:
                            sess_account.proofsinepoch = int(proofsinepoch.text)

                        if len(lastepochmined.text) > 0:
                            sess_account.lastepochmined = int(lastepochmined.text)

                        if len(height.text) > 0 or len(balance.text) > 0 or len(proofsinepoch.text) > 0 or len(
                                lastepochmined.text) > 0:
                            sess_account.updated_at = datetime.now()
                            session.commit()

                    # fetch miner history
                    xp_rows = "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr"
                    xp_button_next = "//div[contains(@class, 'address_statsTablesContainer___HxvE')]/div[2]/div[2]/div/div/ul/li[@title='Next Page']/button"
                    data_name_list = ["epoch", "proofssubmitted"]
                    last_epoch = session.query(func.max(MinerHistory.epoch)).filter(MinerHistory.address==account.address).scalar()
                    last_known_kv = ['epoch', f'{last_epoch}'] if last_epoch else []
                    table_data = fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list, last_known_kv)
                    for row in table_data:
                        o = MinerHistory(
                            address=address.text,
                            epoch=int(row['epoch']),
                            proofssubmitted=int(row['proofssubmitted']))
                        session.add(o)
                    session.commit()

                    # fetch payment events
                    xp_rows = "//div[contains(@class, 'eventsTable_inner__HsGHV')]/div[2]/div/div/div/div/div/table/tbody/tr"
                    xp_button_next = "//div[contains(@class, 'eventsTable_inner__HsGHV')]/div[2]/div/div/ul/li[@title='Next Page']/button"
                    data_name_list = ["height", "type", "amount", "sender", "recipient"]
                    last_height = session.query(func.max(PaymentEvent.height)).filter(PaymentEvent.address==account.address).scalar()
                    last_known_kv = ['height', f'{last_height}'] if last_height else []
                    table_data = fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list, last_known_kv)
                    for row in table_data:
                        o = PaymentEvent(
                            address=address.text,
                            height=int(row['height']),
                            type=row['type'],
                            amount=int(round(float(row['amount'].replace(',', '')), 3) * 1000),
                            sender=row['sender'],
                            recipient=row['recipient'])
                        session.add(o)
                    session.commit()

                    print(f"{sess_account.name} crawled")

                except Exception as e:
                    print(f"{e}")
                finally:
                    driver.quit()

        except ProgrammingError:
            print("Try init DB!")
        except Exception as e:
            print(f"{e}")

if __name__ == "__main__":
    sleep(60)
    sleepy_time = Config.SLEEP_MINS
    while True:
        scrape()
        sleep(60 * sleepy_time)

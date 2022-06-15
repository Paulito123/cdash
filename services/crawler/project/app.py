from time import sleep
from sqlalchemy import text, func
from sqlalchemy.exc import ProgrammingError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from models import AccountStat, MinerHistory, PaymentEvent, NetworkStat, Epoch
from database import session, engine
from config import Config
from datetime import datetime


def fetch_0l_table_data(
        driver,
        xp_rows,
        xp_button_next,
        data_name_list,
        last_known_kv,
        update_most_recent=False) -> []:
    """
    :param driver: selenium driver
    :param xp_rows: xpath to tr element of the data table
    :param xp_button_next: xpath to the next button
    :param data_name_list: column names of data table
    :param last_known_kv: column name and value of last known record
    :param update_most_recent: indicate if last row must be rewritten
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
                    if not update_most_recent:
                        break

                output_dict[f"{data_name}"] = f"{v.text}"
                col_index = col_index + 1

            if break_flag and not update_most_recent:
                # break out row iteration
                break
            elif break_flag and update_most_recent:
                # append the row dict to output list
                output_list.append(output_dict)
                # break out row iteration
                break
            else:
                # append the row dict to output list
                output_list.append(output_dict)

        if break_flag:
            # break out of page iterator
            break

        # click and check status of the next button to determine if all data is loaded
        button_next = driver.find_element(By.XPATH, xp_button_next)
        disabled = button_next.get_property('disabled')
        button_next.click()

    return output_list


def scrape_0l_addresses():
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
                    update_most_recent = True
                    table_data = fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list, last_known_kv, update_most_recent)
                    for row in table_data:
                        epoch = int(row['epoch'])
                        id = session.query(MinerHistory.id).filter(
                            MinerHistory.address == account.address,
                            MinerHistory.epoch == epoch).scalar()

                        o = MinerHistory(
                            address=address.text,
                            epoch=epoch,
                            proofssubmitted=int(row['proofssubmitted']))

                        if id:
                            o.id = id
                            session.merge(o)
                        else:
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
                            amount=int(float(row['amount'].replace(',', '')) * 1000),
                            sender=row['sender'],
                            recipient=row['recipient'])
                        session.add(o)
                    session.commit()

                except Exception as e:
                    print(f"{e}")
                finally:
                    driver.quit()

        except ProgrammingError:
            print("Try init DB!")
        except Exception as e:
            print(f"{e}")


def scrape_0l_home():
    exec_host = 'chrome'
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        driver = webdriver.Remote(
            command_executor=f'http://{exec_host}:4444/wd/hub',
            options=chrome_options
        )

        try:
            # fetch network stats
            url = Config.BASE_URL
            driver.get(url)

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[1]/span[1]/span")
            height = int(tmp.text.replace(',', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[1]/span[2]/span")
            epoch = int(tmp.text.replace(',', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[1]/span[3]/span")
            progress = float(tmp.text.replace('%', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[3]/span[1]/span")
            totalsupply = int(tmp.text.replace(',', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[3]/span[2]/span")
            totaladdresses = int(tmp.text.replace(',', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[3]/span[3]/span")
            totalminers = int(tmp.text.replace(',', ''))

            tmp = driver.find_element(By.XPATH, "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[3]/span[4]/span")
            activeminers = int(tmp.text.replace(',', ''))

            id = session.query(NetworkStat.id).first()
            o = NetworkStat(
                height=height,
                epoch=epoch,
                progress=progress,
                totalsupply=totalsupply,
                totaladdresses=totaladdresses,
                totalminers=totalminers,
                activeminers=activeminers)
            if id:
                o.id = id
                session.merge(o)
            else:
                session.add(o)
            session.commit()

            #TODO: Message: stale element reference: element is not attached to the page document
            #      (Session info: chrome=102.0.5005.61)


            # fetch epoch data
            url = Config.BASE_URL + "epochs"
            driver.get(url)

            xp_rows = "//div[contains(@class, 'epochsTable_inner__jRreG')]/div/div/div/div/div/div/table/tbody/tr"
            xp_button_next = "//div[contains(@class, 'epochsTable_inner__jRreG')]/div/div/div/ul/li[@title='Next Page']/button"
            data_name_list = ["epoch", "timestamp", "height", "miners", "proofs", "ppm", "minerspayable",
                              "minerspayableproofs", "validatorproofs", "minerpaymenttotal"]
            last_epoch = session.query(func.max(Epoch.epoch)).scalar()
            last_known_kv = ['epoch', f'{last_epoch}'] if last_epoch else []
            update_most_recent = True
            table_data = fetch_0l_table_data(driver, xp_rows, xp_button_next, data_name_list, last_known_kv, update_most_recent)
            for row in table_data:
                epoch = int(row['epoch'])
                id = session.query(Epoch.id).filter(Epoch.epoch == epoch).scalar()
                height = int(row['height'])

                # 5/28/2022, 5:48:04 PM
                if len(row['timestamp']) > 0:
                    timestamp = datetime.strptime(row['timestamp'], '%-m/%e/%Y, %-I:%M:%S %p')

                if len(row['miners']) > 0:
                    miners = int(row['miners'].replace(',', ''))

                if len(row['proofs']) > 0:
                    proofs = int(row['proofs'].replace(',', ''))

                if len(row['minerspayable']) > 0:
                    minerspayable = int(row['minerspayable'].replace(',', ''))

                if len(row['minerspayableproofs']) > 0:
                    minerspayableproofs = int(row['minerspayableproofs'].replace(',', ''))

                if len(row['validatorproofs']) > 0:
                    validatorproofs = int(row['validatorproofs'].replace(',', ''))

                if len(row['minerpaymenttotal']) > 0:
                    minerpaymenttotal = float(row['minerpaymenttotal'].replace(',', ''))

                o = Epoch(
                    epoch=epoch,
                    timestamp=timestamp,
                    height=height,
                    miners=miners,
                    proofs=proofs,
                    minerspayable=minerspayable,
                    minerspayableproofs=minerspayableproofs,
                    validatorproofs=validatorproofs,
                    minerpaymenttotal=minerpaymenttotal)

                if id:
                    o.id = id
                    session.merge(o)
                else:
                    session.add(o)
            session.commit()

        except Exception as e:
            print(f"{e}")
        finally:
            driver.quit()

    except ProgrammingError:
        print("Houston, we have a problem...")
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    initial_sleep = int(Config.INITIAL_SLEEP_SECS)
    print(f"[{datetime.now()}] Waiting {initial_sleep} secs")
    sleep(initial_sleep)
    sleepy_time = int(Config.SLEEP_MINS)
    while True:
        print(f"[{datetime.now()}] Begin crawling...")
        scrape_0l_home()
        scrape_0l_addresses()
        print(f"[{datetime.now()}] End crawling. Sleep {sleepy_time} minutes.")
        sleep(60 * sleepy_time)

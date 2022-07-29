import os
import requests
from time import sleep
from sqlalchemy import text, func
# from sqlalchemy.exc import ProgrammingError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from models import AccountStat, MinerHistory, PaymentEvent, NetworkStat, Epoch, ChainEvent, EventLog
from database import session
from config import Config
from datetime import datetime
from agents import Emoji, Telegram


def date_format_pad_awan(strdate) -> str:
    if len(strdate) == 0:
        return strdate

    outputstr = strdate
    if outputstr.index('/') == 1:
        outputstr = '0' + outputstr

    if outputstr[3:].index('/') == 1:
        outputstr = outputstr[:3] + '0' + outputstr[3:]

    if outputstr[15:].index(':') == 1:
        outputstr = outputstr[:12] + '0' + outputstr[12:]

    return outputstr


def get_proofs_per_epoch(address):
    try:
        api_url = "https://0lexplorer.io:444/epochs/proofs/" + address
        result = requests.get(api_url, timeout=10).json()
    except Exception as e:
        print(f"[{datetime.now()}]:{e}")
        result = []
    return result


def get_chain_events(address, start, limit):
    try:
        api_url = f"https://0lexplorer.io/api/proxy/node/account-transactions?type=Miner&address={address}&start={start}&limit={limit}"
        result = requests.get(api_url, timeout=10).json()
    except Exception as e:
        print(f"[{datetime.now()}]:{e}")
        result = []
    return result['result']


def get_payment_events(address, start, limit):
    try:
        api_url = f"https://0lexplorer.io/api/proxy/node/events?address={address}&start={start}&limit={limit}"
        result = requests.get(api_url, timeout=10).json()
    except Exception as e:
        print(f"[{datetime.now()}]:{e}")
        result = []
    return result['result']


def fetch_0l_table_data(
        driver,
        xp_rows,
        xp_button_next,
        data_name_list,
        last_known_kv,
        update_most_recent=False,
        sleep_after_click=0) -> []:
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
        WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_rows))
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
        if sleep_after_click > 0:
            sleep(sleep_after_click)

    return output_list


# def fetch_0l_table_row(
#         driver,
#         xp_rows,
#         xp_button_next,
#         data_name_list) -> {}:
#     """
#     :param driver: selenium driver
#     :param xp_rows: xpath to tr element of the data table
#     :param data_name_list: column names of data table
#     :return: a dictionary
#     """
#     output_row = {}
#
#     # Wait for the page to load
#     WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_rows))
#     WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_button_next))
#
#     # var used to keep track of loops
#     max_loops = 3
#
#     # get table rows by xpath
#     rows = driver.find_elements(By.XPATH, xp_rows)
#
#     # iterate data row by row
#     for row in rows:
#         if max_loops == 0:
#             break
#
#         # discard empty rows
#         if len(row.find_elements(By.TAG_NAME, "td")[0].text) == 0:
#             max_loops = max_loops - 1
#             continue
#
#         # iterate columns
#         col_index = 0
#         for data_name in data_name_list:
#             v = row.find_elements(By.TAG_NAME, "td")[col_index]
#
#             output_row[f"{data_name}"] = f"{v.text}"
#             col_index = col_index + 1
#
#         break
#
#     return output_row


def fetch_epoch_data(
        driver,
        xp_rows,
        xp_button_next,
        data_name_list,
        last_known_epoch=0,
        epochs_in_db=0) -> []:
    """
    :param driver: selenium driver
    :param xp_rows: xpath to tr element of the data table
    :param xp_button_next: xpath to the next button
    :param data_name_list: column names of data table
    :param last_known_epoch: the epoch that is currently running
    :param epochs_in_db: The last epoch registered in the db
    :return: list of dictionaries
    """
    output_list = []

    # Wait for the page to load
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_rows))
    WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, xp_button_next))

    # var used to keep track of when next button is disabled
    disabled = False
    break_threshold = 2
    if epochs_in_db >= (last_known_epoch - 1):
        # only few rows need to be loaded
        break_flag = 0
    else:
        # all rows need to be loaded
        break_flag = -1

    # Crawling table pages
    while not disabled:
        # take time for page to load
        sleep(5)
        # get table rows by xpath
        rows = driver.find_elements(By.XPATH, xp_rows)

        # iterate data row by row
        for row in rows:
            # discard empty rows
            if len(row.find_elements(By.TAG_NAME, "td")[0].text) == 0:
                # Skip row when empty
                continue
            elif break_flag >= 0:
                # Add iteration to break_flag
                break_flag = break_flag + 1

            # iterate columns
            col_index = 0
            output_dict = {}
            for data_name in data_name_list:
                v = row.find_elements(By.TAG_NAME, "td")[col_index]
                output_dict[f"{data_name}"] = f"{v.text}"
                col_index = col_index + 1

            output_list.append(output_dict)

            if break_flag == break_threshold:
                # break out row iteration
                break

        if break_flag == break_threshold:
            # break out of page iterator
            break

        # click and check status of the next button to determine if all data is loaded
        button_next = driver.find_element(By.XPATH, xp_button_next)
        disabled = button_next.get_property('disabled')
        button_next.click()
        sleep(5)

    return output_list


def iterate_0l_addresses():
    exec_host = 'chrome'
    try:
        # Fetch the account list
        accounts = session.query(AccountStat).all()

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
                result = get_proofs_per_epoch(account.address)
                for epoch_obj in result:
                    epoch = int(epoch_obj['epoch'])
                    id = session.query(MinerHistory.id).filter(
                        MinerHistory.address == account.address,
                        MinerHistory.epoch == epoch).scalar()

                    o = MinerHistory(
                        address=account.address,
                        epoch=epoch,
                        proofssubmitted=int(epoch_obj['count']))

                    if id:
                        o.id = id
                        session.merge(o)
                    else:
                        session.add(o)
                session.commit()

                # fetch payment events
                more_to_load = True
                batch_size = 1000
                while more_to_load:
                    max_seq = session.query(func.max(PaymentEvent.seq)).filter(PaymentEvent.address == account.address).scalar()
                    max_seq = max_seq if max_seq else 0
                    result = get_payment_events(account.address, max_seq, batch_size)
                    for pe_obj in result:
                        pe_id = session.query(PaymentEvent.id).filter(PaymentEvent.address == account.address, PaymentEvent.seq == int(pe_obj['sequence_number'])).scalar()

                        o = PaymentEvent(
                            address=address.text,
                            amount=float(pe_obj['data']['amount']['amount']) / 1000000,
                            currency=pe_obj['data']['amount']['currency'],
                            _metadata=pe_obj['data']['metadata'],
                            sender=pe_obj['data']['sender'],
                            recipient=pe_obj['data']['receiver'],
                            type=pe_obj['data']['type'],
                            transactionkey=pe_obj['key'],
                            seq=int(pe_obj['sequence_number']),
                            height=int(pe_obj['transaction_version'])
                            )

                        if pe_id:
                            o.id = pe_id
                            session.merge(o)
                        else:
                            session.add(o)

                    session.commit()

                    if len(result) < batch_size:
                        more_to_load = False

            except Exception as f:
                error_message = f"[{datetime.now()}]:{f}"[:5000]
                try:
                    jobname = os.path.basename(__file__)[:500]
                    o = EventLog(event_source=jobname, type="Application error 2", message=error_message)
                    session.add(o)
                    session.commit()
                except Exception as e:
                    print(f"{error_message}")
                    print(f"{e}")
            finally:
                driver.quit()

    except Exception as f:
        error_message = f"[{datetime.now()}]:{f}"[:5000]
        try:
            jobname = os.path.basename(__file__)[:500]
            o = EventLog(event_source=jobname, type="Application error 1", message=error_message)
            session.add(o)
            session.commit()
        except Exception as e:
            print(f"{error_message}")
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

            heightxpath = "//div[contains(@class, 'index_topStatsInner__YRWuI')]/div[1]/span[1]/span"
            WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.XPATH, heightxpath))
            tmp = driver.find_element(By.XPATH, heightxpath)
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

            nid = session.query(NetworkStat.id).first()
            o = NetworkStat(
                height=height,
                epoch=epoch,
                progress=progress,
                totalsupply=totalsupply,
                totaladdresses=totaladdresses,
                totalminers=totalminers,
                activeminers=activeminers)
            if nid:
                o.id = nid[0]
                session.merge(o)
            else:
                session.add(o)
            session.commit()

            # fetch epoch data
            url = "https://0lexplorer.io/epochs"
            driver.get(url)

            xp_rows = "//div[contains(@class, 'epochsTable_inner__jRreG')]/div/div/div/div/div/div/table/tbody/tr"
            xp_button_next = "//div[contains(@class, 'epochsTable_inner__jRreG')]/div/div/div/ul/li[@title='Next Page']/button"
            data_name_list = ["epoch", "timestamp", "height", "miners", "proofs", "ppm", "minerspayable",
                              "minerspayableproofs", "validatorproofs", "minerpaymenttotal"]
            last_epoch = session.query(func.max(NetworkStat.epoch)).scalar()
            last_epoch = last_epoch if last_epoch else 0
            epochs_in_db = session.query(func.count(Epoch.epoch)).scalar()
            epochs_in_db = epochs_in_db if epochs_in_db else 0
            table_data = fetch_epoch_data(driver, xp_rows, xp_button_next, data_name_list, last_epoch, epochs_in_db)
            for row in table_data:
                epoch = int(row['epoch'])
                height = int(row['height'])

                timestamp = None
                if len(row['timestamp']) > 0:
                    timestamp = datetime.strptime(date_format_pad_awan(row['timestamp']), '%m/%d/%Y, %H:%M:%S %p')

                miners = None
                if len(row['miners']) > 0:
                    miners = int(row['miners'].replace(',', ''))

                proofs = None
                if len(row['proofs']) > 0:
                    proofs = int(row['proofs'].replace(',', ''))

                minerspayable = None
                if len(row['minerspayable']) > 0:
                    minerspayable = int(row['minerspayable'].replace(',', ''))

                minerspayableproofs = None
                if len(row['minerspayableproofs']) > 0:
                    minerspayableproofs = int(row['minerspayableproofs'].replace(',', ''))

                validatorproofs = None
                if len(row['validatorproofs']) > 0:
                    validatorproofs = int(row['validatorproofs'].replace(',', ''))

                minerpaymenttotal = None
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

                eid = session.query(Epoch.id).filter(Epoch.epoch == epoch).scalar()
                if eid:
                    o.id = eid
                    session.merge(o)
                else:
                    session.add(o)
                session.commit()

        except Exception as f:
            error_message = f"[{datetime.now()}]:{f}"[:5000]
            try:
                jobname = os.path.basename(__file__)[:500]
                o = EventLog(event_source=jobname, type="Application error 2", message=error_message)
                session.add(o)
                session.commit()
            except Exception as e:
                print(f"{error_message}")
                print(f"{e}")
        finally:
            driver.quit()

    except Exception as f:
        error_message = f"[{datetime.now()}]:{f}"[:5000]
        try:
            jobname = os.path.basename(__file__)[:500]
            o = EventLog(event_source=jobname, type="Application error 1", message=error_message)
            session.add(o)
            session.commit()
        except Exception as e:
            print(f"{error_message}")
            print(f"{e}")


if __name__ == "__main__":
    initial_sleep = int(Config.INITIAL_SLEEP_SECS)
    print(f"[{datetime.now()}] Waiting {initial_sleep} secs")
    sleep(initial_sleep)
    sleepy_time = int(Config.SLEEP_MINS)
    while True:
        print(f"[{datetime.now()}] Begin crawling 0L home...")
        scrape_0l_home()
        print(f"[{datetime.now()}] Begin crawling addresses...")
        iterate_0l_addresses()
        print(f"[{datetime.now()}] End crawling. Sleep {sleepy_time} minutes.")
        sleep(60 * sleepy_time)

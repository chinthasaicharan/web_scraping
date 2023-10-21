import datetime
import os
import re
import shutil
import urllib
from enum import Enum
from datetime import datetime as dt
from time import sleep
import json
import undetected_chromedriver as uc

# declaring config file
import configparser
import requests
import telegram

# SOCKS_PORT = 9050
# TOR_PATH = os.path.normpath(os.getcwd() + "\\Tor\\tor\\tor.exe")
# tor_process = stem.process.launch_tor_with_config(
#     config={
#         'SocksPort': str(SOCKS_PORT),
#     },
#     init_msg_handler=lambda line: print(line) if re.search('Bootstrapped', line) else False,
#     tor_cmd=TOR_PATH
# )
# PROXIES = {
#     'http': 'socks5://127.0.0.1:9050',
#     'https': 'socks5://127.0.0.1:9050'
# }
# getting config file using configparser
config_obj = configparser.ConfigParser()
config_obj.read('config.ini')

# Web-driver path
PATH = config_obj['driver_path']['PATH']

# importing reusable functions
from reused import initImage, end_datetime_caliculator, format_to_text, return_text, handle_error, \
    clean_link, \
    load_db, reclean_url

# for zip file name
now = dt.now()
today = now.date()
time_now = now.time().strftime('%H_%M_%S')


def set_image_folders(website_name):
    initImage(f'{website_name}')
    initImage(f'{website_name}/images')


# headers for browser

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


# Step 1
# Importing the main database file

class Deal(Enum):
    deal_id = 0
    deal_source_website = 1
    deal_source_website_url = 2
    deal_title = 3
    deal_store = 4
    deal_url = 5
    deal_url_cleaned = 6
    deal_views = 7
    deal_likes = 8
    deal_hotness = 9
    deal_original_price = 10
    deal_price = 11
    deal_discount_percentage = 12
    deal_start_date = 13
    deal_start_time = 14
    deal_end_date = 15
    deal_end_time = 16
    deal_is_hot = 17
    deal_is_active = 18
    deal_category = 19
    deal_image = 20
    deal_is_featured = 21
    deal_short_description = 22
    deal_description = 23
    record_creation_datetime = 24
    record_updation_datetime = 25
    issue_found = 26
    issue_details = 27
    deal_found = 28


column_names = ['deal_source_website',
                'deal_source_website_url',
                'deal_title',
                'deal_store',
                'deal_url',
                'deal_url_cleaned',
                'deal_views',
                'deal_likes',
                'deal_hotness',
                'deal_original_price',
                'deal_price',
                'deal_discount_percentage',
                'deal_start_date',
                'deal_start_time',
                'deal_end_date',
                'deal_end_time',
                'deal_is_hot',
                'deal_is_active',
                'deal_category',
                'deal_image',
                'deal_is_featured',
                'deal_short_description',
                'deal_description',
                'record_creation_datetime',
                'record_updation_datetime',
                'issue_found',
                'issue_details',
                'deal_found'
                ]

# connecting to MYSQL DB

cursor, connection = load_db(config_obj['main']['DB_NAME'])


def initialize_browser(website_name):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    if config_obj[f'{website_name.upper()}_CONFIG'][f'{website_name.upper()}_SCRAPE_HEADLESS'].lower() == 'yes':
        options.add_argument('--headless')

    # using browser object
    browser = uc.Chrome(driver_executable_path=PATH, use_subprocess=True, options=options)
    return browser


def deal_found_to_zero(name):
    # making all deals deal_found = '0'
    # to find out newly updated deals

    cursor.execute(f"UPDATE `deals_scrapped_data` SET `deal_found` = '0' WHERE 'deal_source_website' = '{name}';")
    connection.commit()


def update_or_add_deals(deals, add_func):
    # dividing deals into new and to_be_updated
    for i in deals:
        sleep(6)
        query_1 = f"SELECT * FROM `deals_scrapped_data` WHERE deal_source_website_url = '{i['deal_source_website_url']}'"
        cursor.execute(query_1)
        same_deals = cursor.fetchall()
        print("Scraping: " + str(deals.index(i)) + '/' + str(len(deals)))
        if len(same_deals) == 0:
            try:
                deal = add_func(i)
                print(f'deal added : {i["deal_title"]}')
                if deal is not None:
                    insert_data(deal)
            except Exception as e:
                print(e)

        else:
            update_item(i, same_deals[0])


def insert_data(deal):
    data_str = "\', \'".join(str(i).replace("'", r'\'') for i in deal)
    data_str = remove_emojis(data_str)
    q = f'''INSERT INTO deals_scrapped_data({', '.join(column_names)}) VALUES('{data_str}')'''
    # # print(q)
    cursor.execute(q)
    connection.commit()
    print(f'Deal inserted : {deal[2]}')


def clean_description(description):
    links_to_be_removed = config_obj['main']['bad_links'].split()
    for i in links_to_be_removed:
        description = str(description).replace(i, 'www.dealstobuy.in')
    return description


def issue_check(title, description, deal_price, original_price):
    '''

    Parameters
    ----------
    title
    description

    Returns
    issue_details,issue_found

    '''
    keywords = config_obj['DESIDIME_CONFIG']['FILTER_WORDS_DESIDIME'].split()
    issue_details = []
    issue_found = 'no'
    for i in keywords:
        if i in title.lower():
            issue_details.append(f"{i} found in TITLE")
            issue_found = "yes"
        if i in description.lower():
            issue_details.append(f"'{i}' found in DESCRIPTION")
            issue_found = "yes"
    if deal_price in [0, '0', None]:
        issue_found = 'yes'
        issue_details.append('Issue found in DEAL PRICE')
    if original_price in [0, '0', None]:
        issue_found = 'yes'
        issue_details.append('Issue found in ORIGINAL PRICE')

    return issue_details, issue_found


# Update item in database
# takes new deal from 'deals' and old deal from 'database'
def update_item(new, old):
    '''
    Updates the deal in the database

    Parameters
    ----------
    new - new deal ( dict)
    old -  old deal (list)

    Returns
    -------

    '''
    # if no data change . only setting deal_found = '1
    if (new['deal_likes'] == old[Deal.deal_likes.value] and
            new['deal_hotness'] == old[Deal.deal_hotness.value] and
            new['deal_is_hot'] == old[Deal.deal_is_hot.value] and
            new['deal_end_date'] == old[Deal.deal_end_date.value] and
            new['deal_end_time'] == old[Deal.deal_end_time.value] and
            new['featured'] == old[Deal.deal_is_featured.value]):
        q = f"UPDATE `deals_scrapped_data` SET `deal_found` = `1` WHERE `deal_id` = '{old[Deal.deal_id.value]}'"
        cursor.execute(q)
        connection.commit()
    # if data change . Updating new data and also deal_updation_datetime
    else:
        updated_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        q = f"UPDATE `deals_scrapped_data` SET `deal_found` = '1', `deal_likes` = '{new['deal_likes']}',`deal_hotness` = '{new['deal_hotness']}', `deal_is_hot` = '{new['deal_is_hot']}', `record_updation_datetime` = '{updated_datetime}', `deal_end_date`='{new['deal_end_date']}', `deal_end_time`='{new['deal_end_time']}', `deal_is_featured` = '{new['deal_is_featured']}' WHERE `deal_id` = '{old[Deal.deal_id.value]}'"
        cursor.execute(q)
        connection.commit()
    print(f'updated: {old[Deal.deal_title.value]}')


# sending telegram alert for scraping error  or no founded deals
def scraping_error_check(website_name):
    cursor.execute(
        f'''
        SELECT * FROM `deals_scrapped_data` WHERE `deal_source_website` = '{website_name}' AND `deal_found` = '1';
        ''')
    all_found_deals = cursor.fetchall()
    # if no new deals found
    if len(all_found_deals) == 0:
        system_alert('error', f'0 deals scrapped in script --> {website_name}')
    else:
        system_alert('info', f'{len(all_found_deals)} deals added/updated to the database from {website_name}')


def system_alert(alert_type, message):
    '''
    Sends alerts
    Parameters
    ----------
    alert_type
    message

    Returns
    -------

    '''
    telegram.send_telegram_message(alert_type, message)


#
# send_telegram_message('Error in Scraping ☠️. \n NO NEW DEALS FOUND \n', config_obj['main']['chat_id'],
#                       config_obj['main']['bot_api_key'])

def remove_emojis(text):
    '''

    Parameters
    ----------
    text

    Returns
    -------
    Removes emojis from the text

    '''
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", re.UNICODE)
    return re.sub(emoji_pattern, '', text)


def db_to_zip():
    cursor_ = connection.cursor(dictionary=True)
    q = 'SELECT * FROM final_deals'
    cursor_.execute(q)
    result = cursor_.fetchall()

    # outputting to the file
    string = json.dumps(result, indent=4, sort_keys=True, default=str)

    # writing to a json file
    jsonFile = open(f"C:/web_scraping/output/output_{today}_{time_now}.json", "w")
    jsonFile.write(string)
    jsonFile.close()

    # zipping file
    shutil.make_archive(f'output_zip_{today}_{time_now}', 'zip', 'output')
    os.remove(f'output/output_{today}_{time_now}.json')

import datetime
import urllib
from enum import Enum
import mysql.connector.errors
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from time import sleep
import pandas as pd
import urllib.parse as decoder
import re
import timeout_function_decorator
import sqlite3
import undetected_chromedriver as uc
from lxml import etree
import configparser
import requests

config_obj = configparser.ConfigParser()
config_obj.read('config.ini')

from reused import initImage, end_datetime_caliculator, format_to_text, return_text, handle_error, \
    clean_link, \
    load_db, reclean_url
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


# connecting to MYSQL DB

# cursor, connection = load_db(config_obj['main']['DB_NAME'])

# open the browser
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
options.add_argument('--disable-dev-shm-usage')
if config_obj['DESIDIME_CONFIG']['DESIDIME_SCRAPE_HEADLESS'].lower() == 'yes':
    options.add_argument('--headless')

PATH = config_obj['driver_path']['PATH']
# using browser object
browser = uc.Chrome(driver_executable_path=PATH, use_subprocess=True, options=options)

@timeout_function_decorator.timeout(30)
def scrape_tatacliq(url):
    browser.get(url)
    soup = bs(browser.page_source,'html5lib')
    try:
        title = soup.find('h1')
        print(title.text)
        price = soup.find('h3')
        price(price.text)
    except Exception as e:
        print(e)
        return None

scrape_tatacliq('https://www.tatacliq.com/omron-hem-7156-digital-blood-pressure-monitor-with-360-degree-accuracy-wrap-white/p-mp000000009127753')
browser.quit()
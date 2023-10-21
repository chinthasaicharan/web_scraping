
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

# declaring config file
import configparser
import requests

from reused import initImage, end_datetime_caliculator, format_to_text, return_text, handle_error, \
    clean_link, \
    load_db, reclean_url

# getting config file using configparser
config_obj = configparser.ConfigParser()
config_obj.read('config.ini')

# Web-driver path
PATH = config_obj['driver_path']['PATH']


# headers for browser

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

# using browser object
browser = uc.Chrome(driver_executable_path=PATH, use_subprocess=True, options=options)
def scrape_flipkart(url):
    browser.get(url)
    sleep(5)
    dom = etree.HTML(browser.page_source)
    title = dom.xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[1]/h1/span')
    if len(title) == 2:
        print(title[1].text)
    else:
        print(title[0].text)
    try:
        deal_price = dom.xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div[1]/div/div[1]')[0].text

    except:
        deal_price = None
    try:
        original_price = dom.xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div[1]/div/div[2]')[0].text
    except:
        original_price = None

    desc = dom.xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[9]/div[5]')
    print(deal_price, original_price,desc)

# scrape_flipkart('https://www.flipkart.com/blive-baby-boys-graphic-print-cotton-blend-t-shirt/p/itm0167289be3abe?pid=KTBGCK2HTYWAMSMF')
scrape_flipkart('https://www.flipkart.com/hp-deskjet-2723-multi-function-wifi-color-printer-voice-activated-printing-google-assistant-alexa/p/itm2e7e1651d7330?pid=PRNFTXAWBMU9VGTN')
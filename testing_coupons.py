# /*************************************************************************************************
# * This file is Copyright (C) 2022 Recruit NXT Technologies, all rights reserved.
# *     Copyright Recruit NXT Technologies, Property of RecruitNXT Technologies
# *     Copying, cloning or sharing this code is a criminal offence
# *     Copyright 2022, RecruitNXT, All rights reserved.
# *
# *     THIS SOFTWARE CONTAINS CONFIDENTIAL INFORMATION AND TRADE SECRETS OF RECRUITNXT.
# *     USE, DISCLOSURE OR REPRODUCTION IS PROHIBITED WITHOUT THE PRIOR EXPRESS
# *     WRITTEN PERMISSION OF RECRUITNXT.
# *
# *     Program Name       - indiafreestuff_coupons.py
# *     Relative Path      -  web_scraping/indiafreestuff.py
# *     Purpose of Program - To scrape data from indiafreestuff.com
# *     Called by Programs - main.py
# *     Calling Programs   - reused.py
# *     Date Created       -
# *     History            - Updated 31/10/2022
# **************************************************************************************************/
from enum import Enum

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt

from time import sleep
import pandas as pd
import os
import requests
import urllib.parse as decoder
import re
import undetected_chromedriver as uc
from reused import initImage, end_datetime_caliculator, format_to_text, return_text, handle_error, \
    clean_link, \
    load_db, reclean_url
# declaring config file
import configparser

# getting config file using configparser
config_obj = configparser.ConfigParser()
config_obj.read('config.ini')

# Web-driver path
PATH = config_obj['driver_path']['PATH']
cursor, connection = load_db(config_obj['main']['DB_NAME'])
# formatting the date for use in image names
today = dt.now()
date = today.strftime("%Y%m%d")
image_count = 0


##########################################
# Initialization of recurring variables and arrays
##########################################
class Deal(Enum):
    coupon_id = 0
    coupon_title = 1
    coupon_url = 2
    coupon_code = 3
    coupon_created = 4
    image_url = 5
    users_redeemed = 6
    coupon_likes = 7
    record_creation_datetime = 8
    record_updation_datetime = 9


# initializing an erronous links list and data container list
scraped_coupons = []
new_coupons = []

# open the browser
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(PATH, options=options)






# Get all the links from the main page
def get_page(link):
    browser.get(link)
    sleep(5)
    source = browser.page_source
    soup = bs(source, 'html5lib')
    items = soup.find_all('div', class_='product-item')
    try:
        for item in items:
            if item.find('div', class_='label_expired') is None:
                image = item.find('img')['src']
                reference = item.find('a', class_='get-coupon')['data-href-alt']
                web_link = item.find('a', class_='get-coupon')['data-href']
                title = item.find('a', class_='item-title').text
                title = title.replace('\n', '')
                time = item.find('div', class_='inside-more clearfix').text
                time = time.replace('\n', '')
                coupon_code = item.find('div', class_='coupon-code').text
                coupon_code = coupon_code.replace('\n', '')
                likes = item.find('div',class_='thumb-single').find('span').text.replace('\n','').replace(' ','')
                scraped_coupons.append({
                    'coupon_title': title,
                    'coupon_source_url': reference,
                    'coupon_code': coupon_code,
                    'coupon_url': web_link,
                    'coupon_created': time,
                    'image_url': image,
                    'coupon_likes': likes,
                })
    except Exception as e:
        print(e)

#
# # Getting the coupon id's
def add_coupon(item):
    browser.get(item['coupon_source_url'])
    sleep(3)
    try:
        source = browser.page_source
        soup = bs(source, 'html5lib')
        main_div = soup.find('div', class_='product-container')
        desc = main_div.select_one(selector='div.product-container > div.editor-content.product-details-warp')
        new_coupons.append([
            item['coupon_title'],
            item['coupon_source_url'],
            item['coupon_code'],
            item['coupon_url'],
            # store_name,
            None,
            None,
            # expiry_date,
            None,
            # code_required,
            # users_redeemed,
            None,
            None,
            str(desc).replace('desidime', 'dealstobuy'),
            create_time,
            create_time
        ])
    except Exception as e:
        print(f'failed to get id: {e}')
get_page('https://indiafreestuff.in/deals/coupons')
print(scraped_coupons[:5])
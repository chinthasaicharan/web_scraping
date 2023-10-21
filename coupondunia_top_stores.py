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
# *     Program Name       - coupondunia_top_stores.py
# *     Relative Path      -  web_scraping/coupondunia_top_stores.py
# *     Purpose of Program - To scrape data from coupondunia.com
# *     Called by Programs - main.py
# *     Calling Programs   - reused.py
# *     Date Created       -
# *     History            - Updated 31/10/2022
# **************************************************************************************************/
from bs4 import BeautifulSoup as bs, BeautifulSoup

from coupons_scraping import *

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

initImage('coupondunia')
initImage('coupondunia/images')
##########################################
# Initialization of recurring variables and arrays
##########################################

# initializing an erronous links list and data container list

# open the browser
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
if config_obj['coupons']['headless'].lower() == 'yes':
    options.add_argument('--headless')
browser = webdriver.Chrome(PATH, options=options)

# Initializing the list
scraped_coupons = []
all_top_stores = []
new_coupons = []


######################################################
# Main functions here
######################################################

# Get all the links from the main page
def get_stores(link):
    browser.get(link)
    sleep(5)
    source = browser.page_source
    soup = bs(source, 'html5lib')
    top_stores_anchors = soup.find_all('a', class_='tp-store-link')
    for i in top_stores_anchors:
        store_link = 'https://www.coupondunia.in/' + i['href'] + '&tab=coupon'
        all_top_stores.append(store_link)


# Getting the coupon data by each store with store link
def add_coupons_via_store(link):
    browser.get(link)
    store_name = link.split('/')[-1].split('?')[0]
    print(store_name)
    soup = BeautifulSoup(browser.page_source, 'html5lib')
    try:
        coupon_div = soup.find_all('div', class_='ofr-card-wrap revert')
        for coupon in coupon_div:
            if coupon.find('div', class_='exclusive-tag') is None:
                unique_id = coupon['id']
                is_verified = '0'
                try:
                    verified_tag = coupon.find('div', class_='verified-tag')
                    verified_tag.find('svg').decompose()
                    # print(verified_tag.text)

                    if verified_tag is not None:
                        is_verified = '1'
                except:
                    pass
                # print(verified_tag.text)
                try:
                    used_tag = coupon.find('div', class_='used-tag')
                    used_tag.find('svg').decompose()
                    users_redeemed = used_tag.text.strip().split(' ')[0]
                except:
                    users_redeemed = ''
                # print(users_redeemed)
                try:
                    target_url = coupon.find('div', class_='offer-get-code-link cpnbtn')['data-offer-id']
                    print(target_url)
                    target_url = 'https://www.coupondunia.in/load-offer/' + target_url + '&adBlocker=false'
                    browser.get(target_url)
                    sleep(7)
                    target_url = browser.current_url
                    target_url = clean_link(target_url)
                    print(target_url)
                except:
                    target_url = None

                title = coupon.find('div', class_='offer-desc')
                title = title.text.strip()
                # print(title.text)

                description = coupon.find('div', class_='offer-desc-list')

                success = coupon.find('div', class_='success-counter')
                success_rate = success.text.split('%')[0]
                # print(success_rate)
                try:
                    code = coupon.find('div', class_='p1-code')
                    code = code.text
                    code_required = '1'
                except:
                    code = ''
                    code_required = '0'
                # print(code.text)
                create_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                scraped_coupons.append([
                    title.replace("\'", "\'\'"),
                    'coupondunia',
                    link,
                    target_url,
                    unique_id,
                    code,
                    store_name,
                    is_verified,
                    None,
                    '1',
                    None,
                    None,
                    success_rate,
                    code_required,
                    users_redeemed,
                    None,
                    description,
                    create_time,
                    create_time
                ])
    except Exception as e:
        print(e)


get_stores('https://www.coupondunia.in')

for link in all_top_stores:
    add_coupons_via_store(link)


# scrapped_coupons --> list --> contains all coupons scrapped now
# new_coupons --> list --> coupons to be inserted to database


# updating old deals with same deal source website url in database with unique_id and add deals to new_coupons_list
add_update_via_uid(all_coupons=scraped_coupons, coupons_to_insert=new_coupons)


# Inserting New Data (new coupons) into db
insert_data(coupons_to_insert=new_coupons)

# stoping webdriver
browser.quit()

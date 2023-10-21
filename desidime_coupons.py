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
# *     Program Name       - desidime_coupons.py
# *     Relative Path      -  web_scraping/desidime_coupons.py
# *     Purpose of Program - To scrape data from desidime.com
# *     Called by Programs - main.py
# *     Calling Programs   - reused.py
# *     Date Created       -
# *     History            - Updated 31/10/2022
# **************************************************************************************************/
from enum import Enum
import timeout_function_decorator
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup as bs

from coupons_scraping import *

# open the browser
browser = initialize_browser()

# Initializing the lists
scraped_coupons = []
all_top_stores = []
new_coupons = []

######################################################
# Main functions here
######################################################

# Get all the links from the main page
@timeout_function_decorator.timeout(60)
def get_page(link):
    browser.get(link)
    sleep(5)
    source = browser.page_source
    soup = bs(source, 'html5lib')
    stores = soup.find('div', id='topstores-slider')
    top_stores = stores.find_all('a', class_='swiper-slide')
    for store in top_stores:
        link_ = 'https://www.desidime.com' + store['href']
        all_top_stores.append(link_)


# Getting the coupon data by each store with store link
@timeout_function_decorator.timeout(300)
def add_coupon(link):
    store_name = link.split('/')[-1]
    print(store_name)
    browser.get(link)
    response = browser.page_source
    soup = bs(response, "html5lib")
    try:
        all_coupons_div = soup.find('div', id='show_coupons_data')
        all_coupons = all_coupons_div.find_all('div', class_='coupon_item')
        for coupon in all_coupons:
            id = coupon['id']
            title = coupon.find('a', class_='click_coupon_discount_description').text
            source_website_link = 'https://www.desidime.com' + \
                                  coupon.find('a', class_='click_coupon_discount_description')['data-href']
            coupon_url = coupon.find('a', class_='click_coupon_discount_description')['data-href-alt']
            coupon_url = clean_link(coupon_url)
            coupon_url = reclean_url(coupon_url)
            desc = coupon.find('div', class_='coupon-details-d')

            xpath_address = f'//*[@id="{id}"]/div/div[2]/div[1]/ul/li[1]/span[2]/time'

            dom = etree.HTML(str(soup))
            try:
                dtime = dom.xpath(xpath_address)[0].get('datetime')
                verified_dt = dtime.split('T')[0] + ' ' + dtime.split('T')[1].split('+')[0]
                is_verified = '1'
            except:
                verified_dt = None
                is_verified = '0'

            try:
                expiry_date = dom.xpath(f'//*[@id="{id}"]/div/div[2]/div[1]/ul/li[3]/span[2]')[0].text
                expiry_date = dt.strptime(expiry_date[12:].replace('am', 'AM').replace('pm', 'PM'),
                                          '%B %d, %Y, %H:%M %p').strftime('%Y-%m-%d %H:%M:%S')
            except:
                expiry_date = None
            users_redeemed = dom.xpath(f'//*[@id="{id}"]/div/div[2]/div[1]/ul/li[2]/span[2]')[0].text
            users_redeemed = re.findall(r'-?\d+\.?\d*', users_redeemed)[0]
            try:
                c_code = coupon.find('a', class_='get_code_tag').find('span', class_='hide-code').text.strip()
                code_required = 1
            except:
                code_required = 0
                c_code = None
            create_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            scraped_coupons.append([
                title,
                'desidime',
                source_website_link,
                coupon_url,
                id[-6:],
                c_code,
                store_name,
                is_verified,
                verified_dt,
                '1',
                None,
                expiry_date,
                None,
                code_required,
                users_redeemed,
                None,
                desc,
                create_time,
                create_time
            ])
    except Exception as e:
        print(e)


# # Calling everything from above
# ############################################
get_page('https://www.desidime.com/stores')

# getting all coupons with data in add_coupon
for i in all_top_stores:
    add_coupon(i)

# scrapped_coupons --> list --> contains all coupons scrapped now
# new_coupons --> list --> coupons to be inserted to database


# updating old deals with same deal source website url in database with unique_id and add deals to new_coupons_list
add_update_via_uid(all_coupons=scraped_coupons, coupons_to_insert=new_coupons)

# Inserting New Data (new_coupons) into db
insert_data(coupons_to_insert=new_coupons)

# closing browser
browser.quit()

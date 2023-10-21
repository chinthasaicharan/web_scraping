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
from bs4 import BeautifulSoup as bs

from coupons_scraping import *


# open the browser
browser = initialize_browser()

# Initializing the lists
coupons_all = []
new_coupons = []


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
                browser.get(web_link)
                sleep(7)
                web_link = browser.current_url
                web_link = clean_link(web_link)
                title = item.find('a', class_='item-title').text
                title = title.replace('\n', '')
                time = item.find('div', class_='inside-more clearfix').text
                time = time.replace('\n', '')
                coupon_code = item.find('div', class_='coupon-code').text
                coupon_code = coupon_code.replace('\n', '')
                likes = item.find('div', class_='thumb-single').find('span').text.replace('\n', '').replace(' ', '')
                coupons_all.append({
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


# Getting the coupon id's
def add_coupon(item):
    browser.get(item['coupon_source_url'])
    sleep(3)
    try:
        source = browser.page_source
        soup = bs(source, 'html5lib')
        main_div = soup.find('div', class_='product-container')
        desc = main_div.select_one(selector='div.product-container > div.editor-content.product-details-warp')
        create_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        new_coupons.append([
            item['coupon_title'],
            'indiafreestuff',
            item['coupon_source_url'],
            item['coupon_url'],
            None,
            item['coupon_code'],
            None,
            None,
            None,
            '1',
            None,
            None,
            None,
            '1',
            None,
            item['coupon_likes'],
            desc,
            create_time,
            create_time
        ])
    except Exception as e:
        print(f'failed to get id: {e}')


# updates the coupon data



# calling the Get page to get the deals

get_page('https://indiafreestuff.in/deals/coupons')


# coupons_all --> list --> all coupons with some data scrapped from  main page
# # new_coupons --> list --> coupons to be inserted to database

# add or update all coupons

for i in coupons_all:
    query_1 = f"SELECT * FROM `coupons_scrapped_data` WHERE coupon_source_url = '{i['coupon_source_url']}';"
    cursor.execute(query_1)
    same_deals = cursor.fetchall()
    if len(same_deals) == 0:
        # adding new coupons
        add_coupon(i)
        print(f'coupon added :{i["coupon_title"]}')
    else:
        update_coupon(i, same_deals[0])


# # Inserting New Data (new coupons) into db
insert_data(new_coupons)


browser.quit()

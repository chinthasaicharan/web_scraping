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
# *     Program Name       - grabon_coupons.py
# *     Relative Path      -  web_scraping/coupondunia_top_stores.py
# *     Purpose of Program - To scrape data from coupondunia.com
# *     Called by Programs - main.py
# *     Calling Programs   - reused.py
# *     Date Created       -
# *     History            - Updated 31/10/2022
# **************************************************************************************************/

from bs4 import BeautifulSoup as bs, BeautifulSoup

from timeout_function_decorator import timeout

from selenium.webdriver.common.by import By

from coupons_scraping import *

# open the browser
browser = initialize_browser()

# Initializing the list
scraped_coupons = []
all_top_stores = []
new_coupons = []


######################################################
# Main functions here
######################################################

# Get all the links from the main page
@timeout(120)
def get_stores(link):
    browser.get(link)
    sleep(5)
    source = browser.page_source
    soup = bs(source, 'html5lib')
    top_stores_anchors = soup.find_all('a', class_='go-popstore')
    for i in top_stores_anchors:
        store_link = i['href']
        store_name = i['title'].split(' ')[0]
        all_top_stores.append([store_link, store_name])


# Getting the coupon data by each store with store link
@timeout(120)
def add_coupons_via_store(store):
    browser.get(store[0])
    store_name = store[1]

    print(store_name)
    soup = BeautifulSoup(browser.page_source, 'html5lib')
    try:
        coupon_div = soup.find_all('div', class_='gc-box banko')
        for coupon in coupon_div:
            if coupon['data-type'] == 'cp':
                unique_id = coupon['data-cid']
                title = coupon.find('p').text.strip()
                # print(title)
                verified = coupon.find('span', class_='verified')
                is_verified = '0'
                if verified is not None:
                    is_verified = '1'
                try:
                    users = coupon.find('span', class_='usr').find('span').text
                except:
                    users = None
                description = coupon.find('div', class_='gcb-det').find('ul')
                expiry_date = None
                try:
                    end_date = coupon.find('li', class_='visible-lg c-clk').text
                    expiry_date = text_to_expiry_date(end_date)
                except:
                    pass
                # print(expiry_date)
                coupon_code = None
                try:
                    coupon_code = coupon.find('span', class_='cbtn')
                    coupon_code = coupon_code.find('span', class_='visible-lg').text
                    is_code_req = '1'
                except:
                    is_code_req = '0'
                print(coupon_code)
                source_url = f"https://www.grabon.in/coupon-codes/{unique_id}/"
                create_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                scraped_coupons.append([
                    title.replace("\'", "\'\'"),
                    'grabon',
                    source_url,
                    None,  # url
                    unique_id,
                    coupon_code,
                    store_name,
                    is_verified,
                    None,
                    '1',
                    None,
                    expiry_date,
                    None,
                    is_code_req,
                    users,
                    None,
                    description,
                    create_time,
                    create_time
                ])
    except Exception as e:
        print(e)

@timeout(50)
def get_coupon_url(source_url):
    browser = initialize_browser()
    browser.get(source_url)
    source_handle = browser.current_window_handle
    sleep(5)
    goto = browser.find_element(by=By.CLASS_NAME, value='go_c_red')
    goto.click()
    sleep(4)
    url = browser.current_url
    try:
        # get first child window
        all_handles = browser.window_handles
        for handle in all_handles:
            # switch focus to child window
            if handle != source_handle:
                browser.switch_to.window(handle)
                url = browser.current_url
    except:
        pass
    url = clean_link(url)
    browser.close()
    print(url)
    return url

######################################################
# Calling everything from above
#####################################################
# scraping start
# getting all top stores
get_stores('https://www.grabon.in')
print(all_top_stores)

# adding coupons from each store
for store in all_top_stores[:3]:
    try:
        add_coupons_via_store(store)
        browser.quit()
    except:
        pass

# getting coupon_urls for each coupon
print('getting urls')
for i in range(len(scraped_coupons)):
    try:
        scraped_coupons[i][3] = get_coupon_url(scraped_coupons[i][2])
        print(scraped_coupons[i][3])
    except:
        pass

# scrapped_coupons --> list --> contains all coupons scrapped now
# new_coupons --> list --> coupons to be inserted to database

# updating old deals with same deal source website url in database with unique_id and add deals to new_coupons_list
add_update_via_uid(all_coupons=scraped_coupons, coupons_to_insert=new_coupons)

# Inserting New Data (new coupons) into db
insert_data(coupons_to_insert=new_coupons)

browser.quit()

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
# *     Program Name       - dealsheaven.py
# *     Relative Path      -  web_scraping/dealsheaven.py
# *     Purpose of Program - To scrape data from dealsheaven.com
# *     Called by Programs - main.py
# *     Calling Programs   - reused.py , common_functions.py
# *     Date Created       -
# *     History            - Updated 09/12/2022
# **************************************************************************************************/
import timeout_function_decorator

from common_functions import *
from bs4 import BeautifulSoup as bs

set_image_folders('dealsheaven')
browser = initialize_browser('dealsheaven')


today = dt.now()
date_time = today.strftime('%Y%m%d_%H_%M_%S')
image_count = 0

deals = []
deals_to_insert = []


def get_page(link):
    browser.get(link)
    sleep(10)
    soup = bs(browser.page_source, 'html.parser')
    main_div = soup.find('div', id='deal_listing')
    all_deals = main_div.find_all('div')
    for deal_div in list(set(all_deals)):
        try:
            title = deal_div.find('h3')['title']
            source_url = deal_div.find('a')['href']
            original_price = deal_div.find('p', class_='price').text
            deal_price = deal_div.find('p', class_='spacail-price').text.strip()
            try:
                discount = deal_div.find('div', class_='discount').text
                # print(discount)
                discount = discount.replace('%', '')
            except:
                print('error in discount')
                try:
                    discount = (int(deal_price) / int(original_price)) * 100
                except:
                    discount = None
            deal = {
                'deal_source_website': 'desidime',
                'deal_source_website_url': source_url,
                'deal_title': title,
                'deal_store': None,
                'deal_url': None,
                'deal_url_cleaned': None,
                'deal_views': None,
                'deal_likes': None,
                'deal_hotness': None,
                'deal_original_price': original_price,
                'deal_price': deal_price,
                'deal_discount_percentage': discount,
                'deal_start_date': None,
                'deal_start_time': None,
                'deal_end_date': None,
                'deal_end_time': None,
                'deal_is_hot': None,
                'deal_is_active': None,
                'deal_category': None,
                'deal_image': None,
                'deal_is_featured': None,
                'deal_short_description': None,
                'deal_description': None,
                'record_creation_datetime': None,
                'record_updation_datetime': None}
            deals.append(deal)
        except Exception as e:
            print(e)


@timeout_function_decorator.timeout(60)
def add_item(deal):
    global image_count
    link = deal['deal_source_website_url']
    # opening link in browser
    browser.get(link)
    sleep(10)
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    soup = bs(browser.page_source, 'html.parser')
    try:
        product_image = None
        try:
            img_tag = soup.find('div', class_='product-img-inner').find('img')['src']
            image_bytes = requests.get(img_tag,timeout=5)
            response = image_bytes
            # closing requests connection
            image_bytes.close()
            if response:
                with open(f"./dealsheaven/images/IMG_{date_time}_{image_count}_dh.png", 'wb') as f:
                    f.write(image_bytes.content)
            product_image = f"IMG_{date_time}_{image_count}_dh.png"
            image_count += 1
        except:
            print('failed to extract image for this deal')
        view_count = soup.find('div', class_='view-count').text
        view_count = view_count.replace('views', '').strip()
        store = soup.find('div', class_='esite-logo').find('img')['title']
        # print(store)
        description = soup.find('div', id='deal-description').find('ul')
        # print(description)
        redirect_link = soup.find('div', class_='shop-now-button mobile-hide').find('a')['href']
        # print(redirect_link)

        browser.get(redirect_link)
        sleep(5)
        deal_link = browser.current_url
        cleaned_deal_link = clean_link(deal_link)
        cleaned_deal_link = reclean_url(cleaned_deal_link)
        # cleaning links in the description
        # print(cleaned_deal_link)
        description = clean_description(description)

        # issue checking
        issue_details, issue_found = issue_check(title=deal['deal_title'], description=description,
                                                 original_price=deal['deal_original_price'],
                                                 deal_price=deal['deal_price'],)

        # appending each new deal to list called deals to insert
        return [
            'dealsheaven',
            link,
            deal['deal_title'],
            store,
            deal_link,
            cleaned_deal_link,
            view_count,
            None,
            None,
            deal['deal_original_price'],
            deal['deal_price'],
            deal['deal_discount_percentage'],
            None,
            None,
            None,
            None,
            '1',
            '1',
            None,
            product_image,
            '0',
            None,
            description,
            create_time,
            create_time,
            issue_found,
            ', '.join(issue_details),
            '1'
        ]
    except Exception as e:
        print(f"{e} \n"
              f" error in : {deal['deal_title']}")


# setting dealsheaven deal_found to zero
deal_found_to_zero('dealsheaven')

# getting dealsheaven
get_page('https://dealsheaven.in/')

# print(deals)
update_or_add_deals(deals[:40], add_func=add_item)

# error check
scraping_error_check('dealsheaven')

browser.quit()

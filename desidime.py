
import timeout_function_decorator
from bs4 import BeautifulSoup as bs
# importing common_deal functions
from common_functions import *

# importing reusable functions
from reused import end_datetime_caliculator, format_to_text, return_text, handle_error, \
    clean_link, reclean_url

# formatting the date for use in image names
today = dt.now()
date_time = today.strftime('%Y%m%d_%H_%M_%S')
image_count = 0

set_image_folders('desidime')

browser = initialize_browser('desidime')

# Initializing the list
deals_to_insert = []
error_links = []
new_items = []
items_to_update = []
deals = []


# Get all the links from the main page
# The result will be saved as an array of objects in 'deals'
def get_page(link, time):
    # opening browser
    browser.get(link)
    # waiting to load
    sleep(5)
    # Scrolling the website with interval for 'time' seconds
    for i in range(time):
        browser.execute_script(f"document.getElementById('hidden_deals').scrollIntoView()")
        sleep(5)
    # waiting for final page
    sleep(5)
    source = browser.page_source
    # setting beautiful soup
    soup = bs(source, 'html5lib')

    # getting a list of all currently available deals
    main_div = soup.find('div', id="deals-grid")

    # getting all deals from main div
    list_of_items = main_div.find_all('li', class_='padfix')

    # limiting to 100 deals
    if len(list_of_items) > int(config_obj["DESIDIME_CONFIG"]['DESIDIME_MAX_DEALS_TO_SCRAPE']):
        list_of_items = list_of_items[:int(config_obj["DESIDIME_CONFIG"]['DESIDIME_MAX_DEALS_TO_SCRAPE'])]

    # looping through each deal
    for item in list_of_items:
        try:
            # getting source url
            link_element = item.find('a', href=True)
            link = link_element['href']
            link = f"https://www.desidime.com{link}"
            # getting likes
            likes = None
            try:
                likes_item = item.find('span', class_='post-count')
                likes = format_to_text(likes_item.text)
            except:
                pass
            # getting hot tag
            hot = None
            try:
                hot = item.find('div', class_='ftl pl10')
                hot = '1'
            except:
                pass

            # getting deal hotness
            deal_hotness = None
            try:
                deal_hotness = return_text(
                    item.find('div', class_='deal-box-head').find('span', class_='deal-hot').text)
                deal_hotness = deal_hotness[:-1]
            except:
                pass
            # getting deal price
            deal_price = None
            try:
                deal_price = item.find('div', class_='deal-price').text.strip()
            except:
                pass
            # getting deal percentage
            deal_percent = None
            try:
                deal_percent = item.find('div', class_='deal-discount').text
                deal_percent = deal_percent.replace('%', '').replace('OFF', '').strip()
            except:
                pass
            # getting feature tag
            try:
                featured = item.find('span', class_='tag-feature').text
                featured = '1'
            except:
                featured = '0'
            # The deal title
            title = item.find('div', class_='deal-dsp')

            deal = {
                'deal_source_website': 'desidime',
                'deal_source_website_url': link,
                'deal_title': title.text.strip(),
                'deal_store': None,
                'deal_url': None,
                'deal_url_cleaned': None,
                'deal_views': None,
                'deal_likes': likes,
                'deal_hotness': deal_hotness,
                'deal_original_price': None,
                'deal_price': deal_price,
                'deal_discount_percentage': deal_percent,
                'deal_start_date': None,
                'deal_start_time': None,
                'deal_end_date': None,
                'deal_end_time': None,
                'deal_is_hot': hot,
                'deal_is_active': None,
                'deal_category': None,
                'deal_image': None,
                'deal_is_featured': featured,
                'deal_short_description': None,
                'deal_description': None,
                'record_creation_datetime': None,
                'record_updation_datetime': None}
            deals.append(deal)
        except Exception as e:
            print(e)


# For new item
@timeout_function_decorator.timeout(60)
def add_item(deal):
    global image_count
    link = deal['deal_source_website_url']
    # opening link in browser
    browser.get(link)
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sleep(5)
    try:
        source = browser.page_source
        soup = bs(source, 'html5lib')
        # getting title of the deal
        title = soup.find('h1', class_='f20 mb20 bold').text.strip()

        # getting deal_url
        deal_url = handle_error(
            soup.find('a', class_='buy_now_tag btn-buynow gtm-buynow-tag-top')['href'].split('url=')[1])
        # cleaning for tags
        deal_url = clean_link(deal_url)
        # cleaning for amazon,
        deal_url_cleaned = reclean_url(deal_url)
        # getting deal store
        deal_store = deal_url.split('/')[2].replace('www.', '').split('.')[0]

        # getting view count
        view_count = return_text(soup.find('span', class_='cactions').text)

        # getting product image
        product_image = handle_error(soup.find('a', class_='dealpromoimage').find('img')['data-src'])
        image_bytes = requests.get(product_image, headers=headers)
        if image_bytes.status_code:
            with open(f"./desidime/images/IMG_{date_time}_{image_count}_dm.png", 'wb') as f:
                f.write(image_bytes.content)
        product_image = f"IMG_{date_time}_{image_count}_dm.png"
        image_count += 1
        if deal['deal_price'] is None:
            try:
                deal['deal_price'] = soup.find('div',class_='dealprice').find('span').text
            except:
                pass
        # getting original price
        original_price = None
        try:
            original_price = \
                return_text(soup.find('div', class_='dealpercent').find('span', class_='line-through').text).split('.')[
                    0]
        except:
            pass
        # getting categories
        groups = []
        group_list = handle_error(soup.find_all('a', class_='gtm-fp-groups'))
        start_date = None
        for group in group_list:
            text = group.text
            text = format_to_text(text)
            groups.append(text)
            start_date = soup.find('span', class_='cicon').find('time')['datetime']
            start_date = start_date.split('T')[0]
        # start date and end date
        try:
            end_datetime = soup.find('span', class_='expirytime').text
            end_date_arr = end_datetime.replace('\n', ' ').split(' ')
            end_date_arr = [i for i in end_date_arr if i != '']
            end_date, end_time = end_datetime_caliculator(end_date_arr)
        except:
            end_date = None
            end_time = None

        # getting description
        try:
            description = soup.find('div', class_='mainpost usercomment')
            try:
                images = description.find_all('img')
                desc_images = []
                for image in images:
                    image_bytes = requests.get(image['src'])
                    if image_bytes.status_code == 200:
                        with open(f"./desidime/images/IMG_{date_time}_{image_count}_dm.png", 'wb') as f:
                            f.write(image_bytes.content)
                        img_name = f"IMG_{date_time}_{image_count}_dm.png"
                        image_count += 1
                        desc_images.append(img_name)
            except:
                desc_images = []
            for image in desc_images:
                description.img.replace_with("{" + image + "}")
        except:
            description = 'error fetching description'

        # cleaning links in the description

        description = clean_description(description)

        print(f'deal price : {deal["deal_price"]}')
        print(f'or price: {original_price}')
        # issue checking
        issue_details, issue_found = issue_check(title, description,deal_price=deal['deal_price'],original_price=original_price)

        # appending each new deal to list called deals to insert
        deal_data = [
            'desidime',
            link,
            title,
            deal_store,
            deal_url,
            deal_url_cleaned,
            view_count,
            deal['deal_likes'],
            deal['deal_hotness'],
            original_price,
            deal['deal_price'],
            deal['deal_discount_percentage'],
            start_date,
            None,
            end_date,
            end_time,
            deal['deal_is_hot'],
            '1',
            ','.join(groups),
            product_image,
            deal['deal_is_featured'],
            deal['deal_short_description'],
            description,
            create_time,
            create_time,
            issue_found,
            ', '.join(issue_details),
            '1'
        ]
        return deal_data
    except Exception as e:
        print(f'{e} in {deal["deal_title"]}')


############################################
# Calling everything from above
############################################


# making all deals deal_found = '0'
# to find out newly updated deals
deal_found_to_zero('desidime')
# scrapping data from all pages

get_page(config_obj['DESIDIME_CONFIG']['DESIDIME_ALL_DEALS_URL'],
         int(config_obj['DESIDIME_CONFIG']['DESIDIME_DELAY_IN_SCRAPPING']))
# get_page(config_obj['DESIDIME_CONFIG']['DESIDIME_HOT_DEALS_URL'],
#          int(config_obj['DESIDIME_CONFIG']['DESIDIME_DELAY_IN_SCRAPPING']))
# get_page('https://www.desidime.com/discussed',
#          int(config_obj['DESIDIME_CONFIG']['DESIDIME_DELAY_IN_SCRAPPING']))


# removing common deals from all pages(duplicate_deals)
dup_deals = []
for i in deals:
    if i not in dup_deals:
        dup_deals.append(i)
deals = dup_deals


# dividing deals into new and to_be_updated

update_or_add_deals(deals[:40], add_func=add_item)

# telegram alert with error checking
scraping_error_check('desidime')


browser.quit()




















# exception handling and setting inactive for not founded deals

# cursor.execute('''SELECT * FROM `deals_scrapped_data` WHERE `deal_source_website` = 'desidime' AND `deal_found` = '1';''')
# all_found_deals = cursor.fetchall()
# if len(all_found_deals) != 0:
#     # setting deals to inactive if it is not found and active before
#
#     all_query = "UPDATE `deals_scrapped_data` SET `deal_is_active` = '0' WHERE `deal_found` = '0' AND `deal_is_active` = '1';"
#     cursor.execute(all_query)
#     connection.commit()
#     print("deals deactivated")




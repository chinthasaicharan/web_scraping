import timeout_function_decorator

# importing reusable functions
from reused import initImage, format_to_text, return_text, handle_error, clean_link, load_db, \
    reclean_url
from common_functions import *
from bs4 import BeautifulSoup as bs

# formatting the date for use in image names
today = dt.now()
date_time = today.strftime('%Y%m%d_%H_%M_%S')
image_count = 0

set_image_folders('indiafreestuff')

# initializing an erroreous links list and data container list

# open the browser
browser = initialize_browser('indiafreestuff')

# Initializing the list
new_items = []
items_to_update = []
deals = []
deals_to_insert = []
error_links = []


######################################################
# Main functions here
######################################################

# Get all the links from the main page
@timeout_function_decorator.timeout(120)
def get_page(page, status):
    browser.get(page)
    source = browser.page_source
    soup = bs(source, 'html5lib')
    product_items = soup.find_all('div', class_='product-item')
    for product in product_items:
        try:
            link_ = handle_error(product.find('a', class_='item-title')['href'])
            title = return_text(product.find('a', class_='item-title').text)
            hotness = handle_error(return_text(product.find('div', class_='thumb-single').text))
            original_price = handle_error(return_text(product.find('div', class_='old-price').text))
            deal_price = handle_error(return_text(product.find('div', class_='new-price').text))
            deal_percent = handle_error(
                return_text(product.find('div', class_='off-discount').text).replace('%', '').replace('Off',
                                                                                                      ''))
            try:
                product_image = handle_error(product.find('div', class_='product-img').find('img')['src'])
            except:
                product_image = product.find('a', class_='product-img').find('img')['data-original']
            short_desc = handle_error(product.find('span', class_='inside-text').text)
            likes = product.find('div', class_='thumb-single')
            likes = handle_error(likes.text.replace('\n', ''))
            deal = {
                'deal_source_website': 'indiafreestuff',
                'deal_source_website_url': link_,
                'deal_title': title,
                'deal_store': None,
                'deal_url': None,
                'deal_url_cleaned': None,
                'deal_views': None,
                'deal_likes': likes,
                'deal_hotness': hotness,
                'deal_original_price': original_price,
                'deal_price': deal_price,
                'deal_discount_percentage': deal_percent,
                'deal_start_date': None,
                'deal_start_time': None,
                'deal_end_date': None,
                'deal_end_time': None,
                'deal_is_hot': status,
                'deal_is_active': None,
                'deal_category': None,
                'deal_image': product_image,
                'deal_is_featured': None,
                'deal_short_description': short_desc,
                'deal_description': None,
                'record_creation_datetime': None,
                'record_updation_datetime': None
            }
            deals.append(deal)
        except:
            print('error with ' + str(product_items.index(product)))


@timeout_function_decorator.timeout(60)
def add_item(deal):
    '''
    Adds new deal to new_data after scraping all data
    Parameters
    ----------
    deal

    Returns
    -------

    '''
    global image_count
    link = deal['deal_source_website_url']
    try:
        response = requests.get(link, headers=headers)
        source = response.text
        soup = bs(source, 'html5lib')
        image_link = deal['deal_image']
        image_bytes = requests.get(image_link, headers=headers)
        if image_bytes.status_code:
            with open(f"./indiafreestuff/images/IMG_{date_time}_{image_count}_in.png", 'wb') as f:
                f.write(image_bytes.content)
        image = f"IMG_{date_time}_{image_count}_in.png"
        image_count += 1
        view_count = 0
        product_link = handle_error(
            soup.find('div', class_='editor-content product-details-warp').find('ol').find('a')['href'])

        browser.get(product_link)
        sleep(10)
        # getting deal url
        product_link = browser.current_url
        product_link = clean_link(product_link)
        cleaned_url = reclean_url(product_link)
        # getting deal website
        website_name = product_link.split('/')[2].replace('www.', '').split('.')[0]
        # getting deal description
        description = soup.find('div', class_='editor-content product-details-warp')
        description = clean_description(description)
        # issue check
        issue_details, issue_found = issue_check(deal['deal_title'], description,
                                                 original_price=deal['deal_original_price'],
                                                 deal_price=deal['deal_price'], )

        create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        deal_data = [
            deal['deal_source_website'],
            deal['deal_source_website_url'],
            deal['deal_title'],
            website_name,
            product_link,
            cleaned_url,
            view_count,
            deal['deal_likes'],
            deal['deal_hotness'],
            deal['deal_original_price'],
            deal['deal_price'],
            deal['deal_discount_percentage'],
            None,
            None,
            None,
            None,
            deal['deal_is_hot'],
            '1',
            None,
            image,
            '0',
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


deal_found_to_zero('indiafreestuff')

# Program start
get_page(config_obj['INDIAFREESTUFF_CONFIG']['INDIAFREESTUFF_URL'], '0')

get_page(config_obj['INDIAFREESTUFF_CONFIG']['INDIAFREESTUFF_HOT_DEAL_URL'], '1')

# testing code below
# deals = deals[:10]

print(f"length of deals: {len(deals)}")

update_or_add_deals(deals=deals, add_func=add_item)

# error check
scraping_error_check('indiafreestuff')

browser.quit()

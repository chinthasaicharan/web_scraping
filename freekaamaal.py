import timeout_function_decorator
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from common_functions import *

# importing reusable functions
from reused import initImage, format_to_text, return_text, handle_error, clean_link, load_db, \
    reclean_url

# formatting the date for use in image names
today = dt.now()
date_time = today.strftime('%Y%m%d_%H_%M_%S')
image_count = 0

set_image_folders('freekaamaal')

# open the browser
browser = initialize_browser('freekaamaal')


## login
def login():
    browser.get(config_obj['FREEKAAMAAL_CONFIG']['FREEKAAMAAL_LOGIN_URL'])
    email_entry = browser.find_element(by=By.XPATH, value='//*[@id="login_email"]')
    email_entry.send_keys('dojabi9847@botssoko.com')
    pwd_entry = browser.find_element(by=By.XPATH, value='//*[@id="login_pass"]')
    pwd_entry.send_keys('dealsforsa')

    print('PLease login manually')
    for i in range(40):
        print(f'time remaining {60 - i}')
        sleep(1)


# Initializing the list
deals_to_insert = []
new_items = []
deals = []


######################################################
# Main functions here
######################################################
# Get all the links from the main page
@timeout_function_decorator.timeout(60)
def get_page(link):
    browser.get(link)
    sleep(5)
    soup = bs(browser.page_source, 'html5lib')
    # featured deals
    try:
        featured = soup.find('ul', class_='bxslider abc')
        listOfFeaturedItems = featured.find_all('li')
        for item in listOfFeaturedItems:
            link = item.find('a')['href']
            featured = '1'
            title = item.find('p', class_='must-dea-title').text
            title = return_text(title)
            priceContainer = item.find('span', class_='must-price-con')
            original_price = handle_error(priceContainer.find('del').text)
            deal_price = handle_error(priceContainer.find('label').text)
            deal = {
                'deal_source_website': 'freekaamaal',
                'deal_source_website_url': link,
                'deal_title': title,
                'deal_store': None,
                'deal_url': None,
                'deal_url_cleaned': None,
                'deal_views': None,
                'deal_likes': None,
                'deal_hotness': None,
                'deal_original_price': original_price,
                'deal_price': deal_price,
                'deal_discount_percentage': None,
                'deal_start_date': None,
                'deal_start_time': None,
                'deal_end_date': None,
                'deal_end_time': None,
                'deal_is_hot': "0",
                'deal_is_active': None,
                'deal_category': None,
                'deal_image': None,
                'deal_is_featured': featured,
                'deal_short_description': None,
                'deal_description': None,
                'record_creation_datetime': None,
                'record_updation_datetime': None
            }
            deals.append(deal)
    except Exception as e:
        print(f'failed to append deal: {e}')
    # Hot deals
    try:
        otherDeals = soup.find('div', id="homepagedealmain")
        listOfDeals = otherDeals.find_all('div', class_='fkm-deal-boxnew-size fkm-deal-boxpadding')
        for item in listOfDeals:
            title = item.find('p', class_="product-name").text
            title = return_text(title)
            link = item.find('p', class_='product-name').find('a')['href']
            original_price = handle_error(item.find('p', class_='cut-price').text)
            deal_price = handle_error(item.find('p', class_='main-price').text)
            featured = '1'
            deal = {
                'deal_source_website': 'freekaamaal',
                'deal_source_website_url': link,
                'deal_title': title,
                'deal_store': None,
                'deal_url': None,
                'deal_url_cleaned': None,
                'deal_views': None,
                'deal_likes': None,
                'deal_hotness': None,
                'deal_original_price': original_price,
                'deal_price': deal_price,
                'deal_discount_percentage': None,
                'deal_start_date': None,
                'deal_start_time': None,
                'deal_end_date': None,
                'deal_end_time': None,
                'deal_is_hot': '1',
                'deal_is_active': None,
                'deal_category': None,
                'deal_image': None,
                'deal_is_featured': featured,
                'deal_short_description': None,
                'deal_description': None,
                'record_creation_datetime': None,
                'record_updation_datetime': None
            }
            deals.append(deal)

    except Exception as e:
        print(e)


# Function for scraping a page
@timeout_function_decorator.timeout(60)
def add_item(deal):
    global image_count
    create_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        link_ = deal['deal_source_website_url']
        browser.get(link_)
        soup = bs(browser.page_source, 'html5lib')
        sleep(5)
        title = deal['deal_title']
        original_price = deal['deal_original_price']
        deal_price = deal['deal_price']

        image = soup.find('span', class_='product-img').find('img')['src']

        image_bytes = requests.get(image)
        if image_bytes.status_code == 200:
            with open(f"./freekaamaal/images/IMG_{date_time}_{image_count}_fm.png", 'wb') as f:
                f.write(image_bytes.content)
        product_image = f"IMG_{date_time}_{image_count}_fm.png"
        image_count += 1
        view_count = soup.find('p', class_='deal-status').find_all('span')[1].text.split(' ')[0]
        description = soup.find('div', class_='c_editorbox content-desc dl_dsc_to_get')
        # print(description)
        handle_error(description.find('h1').decompose())
        handle_error(description.find('p', class_='deal-status').decompose())
        handle_error(description.find('p', class_='main-pera').decompose())
        handle_error(description.find('div', class_='cb-claimform-wrap').decompose())
        # description.find('p').decompose()
        description_text = description.text
        try:
            images = description.find_all('img')
            desc_images = []
            for image in images:
                image_bytes = requests.get(image['src'])
                if image_bytes.status_code == 200:
                    with open(f"./freekaamaal/images/IMG_{date_time}_{image_count}_fm.png", 'wb') as f:
                        f.write(image_bytes.content)
                    img_name = f"IMG_{date_time}_{image_count}_fm.png"
                    image_count += 1
                    desc_images.append(img_name)
            for image in desc_images:
                description.img.replace_with("{" + image + "}")
        except Exception as e:
            print(e)
            description = "error fetching description"
            description_text = ''
        description = clean_description(description)
        # print(description)
        featured = deal['deal_is_featured']
        linkToFollow = soup.find('a', class_='shop-earn-btn')['href']
        # getting original link
        browser.get(linkToFollow)
        sleep(10)
        product_link = browser.current_url
        product_link_cleaned = clean_link(product_link)
        # product_link_cleaned = reclean_url(product_link)

        # getting deal website
        website_name = product_link_cleaned.split('/')[2].replace('www.', '').split('.')[0]
        try:
            deal_price = int(deal_price.split(' ')[1])
        except:
            deal_price = None

        try:
            original_price = int(original_price.split(' ')[1])
        except:
            original_price = None
        discount_percentage = None
        try:
            discount_percentage = 100 - ((deal_price / original_price) * 100)
        except:
            pass
        likes = None
        try:
            likes = soup.find('label', id='like-count').text[0]
        except:
            pass

        # issue checking
        issue_details, issue_found = issue_check(title, description,deal_price,original_price)

        # adding individual deal data to a list
        deal_data = [
            deal['deal_source_website'],
            deal['deal_source_website_url'],
            title,
            website_name,
            product_link,
            product_link_cleaned,
            view_count,
            likes,
            None,
            original_price,
            deal_price,
            discount_percentage,
            None,
            None,
            None,
            None,
            deal['deal_is_hot'],
            None,
            None,
            product_image,
            featured,
            None,
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
deal_found_to_zero('freekaamaal')

# logging into website
login()

# opening page
get_page(config_obj['FREEKAAMAAL_CONFIG']['FREEKAAMAAL_URL'])

# updating old deals with same deal source website url in database
update_or_add_deals(deals, add_func=add_item)

# error checking
scraping_error_check('freekaamaal')

# stopping the browser
browser.quit()

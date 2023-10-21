# scraping of all websites here
import desidime
import indiafreestuff
import freekaamaal
import dealsheaven
from common_functions import *
import datetime as dt

set_image_folders('output')

now = dt.datetime.now()
today = now.date()
time_now = now.time().strftime('%H_%M_%S')


# clone data from deals_scrapped_data to final_deals table - function
def clone_data(deal_source_website_name):
    def update(new, old):
        """
        Updates Deal : hotness, views,

        Parameters
        ----------
        new - new_deal
        old - old_deal

        Returns None
        -------

        """
        # updating hotness on which is higher\
        deal_likes = old[Deal.deal_likes.value]
        try:
            if int(new[Deal.deal_likes.value]) >= int(old[Deal.deal_likes.value]):
                deal_likes = new[Deal.deal_likes.value]
        except:
            pass
        # updating likes
        deal_hotness = old[Deal.deal_hotness.value]
        if int(new[Deal.deal_hotness.value]) >= int(old[Deal.deal_hotness.value]):
            deal_hotness = new[Deal.deal_hotness.value]

        # updating price
        deal_price = old[Deal.deal_hotness.value]
        if int(new[Deal.deal_price.value]) >= int(old[Deal.deal_price.value]):
            deal_hotness = new[Deal.deal_price.value]

        # updating views on which is higher
        deal_views = old[Deal.deal_views.value]
        if int(old[Deal.deal_views.value]) <= int(new[Deal.deal_views.value]):
            deal_views = new[Deal.deal_views.value]

        # updates is_active only if deal active in database
        deal_is_active = old[Deal.deal_is_active.value]
        if old[Deal.deal_is_active.value] == '1':
            deal_is_active = new[Deal.deal_is_active.value]
        # deal is hot
        deal_is_hot = old[Deal.deal_is_hot.value]
        if old[Deal.deal_is_hot.value] == '1':
            deal_is_hot = new[Deal.deal_is_hot.value]
        # updating updation-time

        q = f"UPDATE `{config_obj['main']['OUTPUT_TABLE_NAME']}` SET `deal_likes` = '{deal_likes}',`deal_hotness` = '{deal_hotness}', `deal_views` = '{deal_views}', `deal_price` = '{deal_price}', `deal_is_active` = '{deal_is_active}', `deal_is_hot` = '{deal_is_hot}', `record_updation_datetime` = '{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE `final_deals`.deal_id = '{old[Deal.deal_id.value]}'"
        cursor.execute(q)
        connection.commit()
        print(f'updated: {old[Deal.deal_title.value]}')

    def create(new_deal):
        '''
        Creates a new deal in the output database
        Parameters
        ----------
        new_deal

        Returns
        -------

        '''
        data_str = "\' , \'".join([str(k).replace("'", r'\'') for k in new_deal])
        # print(data_str)
        query_insert = f'''INSERT INTO `final_deals` VALUES('{data_str}')'''
        cursor.execute(query_insert)
        connection.commit()
        print(f'created: {new_deal[Deal.deal_title.value]}')

    # code starts

    dt_2hr_before = dt.datetime.now() - dt.timedelta(hours=2)
    dt_2hr_before = dt_2hr_before.strftime('%Y-%m-%d %H:%M:%S')

    # getting last 2hr data

    query = f"SELECT * FROM `deals_scrapped_data` WHERE deal_source_website = '{deal_source_website_name}' AND (record_creation_datetime >= '{dt_2hr_before}' OR record_updation_datetime >= '{dt_2hr_before}');"
    cursor.execute(query)
    last_2hr_data = cursor.fetchall()

    # querying last 2 hr data with last 10 days data

    dt_10days_before = dt.datetime.now() - dt.timedelta(days=10)
    dt_10days_before = dt_10days_before.strftime('%Y-%m-%d %H:%M:%S')

    for deal in last_2hr_data:

        # for deal source website and record creation and updation time
        source_url = (deal[Deal.deal_source_website_url.value]).replace("'", r'\'')
        query_1 = f"SELECT * FROM `final_deals` WHERE deal_source_website_url = '{source_url}' AND record_creation_datetime >= '{dt_10days_before}'"
        cursor.execute(query_1)
        deal_source_url_match = cursor.fetchall()
        # checking for matches

        if len(deal_source_url_match) == 0:
            # for deal url and deal_store
            # coming " ' " in SQl syntax so it does not give errors
            deal_url = (deal[Deal.deal_url.value]).replace("'", r'\'')
            query_2 = f"SELECT * FROM `final_deals` WHERE deal_url = '{deal_url}' AND deal_store = '{deal[Deal.deal_store.value]}' AND record_creation_datetime >= '{dt_10days_before}';"
            cursor.execute(query_2)
            deal_url_match = cursor.fetchall()
            # for deal_url_cleaned and deal_store
            deal_url_cleaned = (deal[Deal.deal_url_cleaned.value]).replace("'", r'\'')
            if len(deal_url_match) == 0:
                query_3 = f"SELECT * FROM `final_deals` WHERE deal_url_cleaned = '{deal_url_cleaned}' AND deal_store = '{deal[Deal.deal_store.value]}' AND record_creation_datetime >= '{dt_10days_before}'"
                cursor.execute(query_3)
                deal_url_clean_match = cursor.fetchall()
                if len(deal_url_clean_match) == 0:
                    create(deal)
                else:
                    update(new=deal, old=deal_url_clean_match[0])
            else:
                update(new=deal, old=deal_url_match[0])
        else:
            update(new=deal, old=deal_source_url_match[0])

        # copying images into output/images folder
        initImage("output/images")
        initImage(f"{deal_source_website_name}/images")
        for i in os.listdir(f"{deal_source_website_name}/images"):
            try:
                shutil.copy(f"{deal_source_website_name}/images/{i}", "output/images")
            except:
                print("failed to copy")


# Running the above code

clone_data('desidime')
clone_data('freekaamaal')
clone_data('indiafreestuff')
clone_data('dealsheaven')

# Packing data and images into a dictionary
db_to_zip()

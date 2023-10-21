
import datetime as dt
from enum import Enum
import json
import configparser
from reused import load_db

# getting config file using configparser
config_obj = configparser.ConfigParser()
config_obj.read('config.ini')

now = dt.datetime.now()
today = now.date()
time_now = now.time().strftime('%H_%M_%S')

cursor, connection = load_db(config_obj['main']['DB_NAME'])


class Coupon(Enum):
    coupon_id = 0
    coupon_title = 1
    coupon_source_url = 2
    coupon_url = 3
    coupon_unique_id = 4
    coupon_code = 5
    coupon_store = 6
    verified_datetime = 7
    coupon_start_date = 8
    coupon_end_date = 9
    coupon_success_rate = 10
    coupon_is_code_required = 11
    users_redeemed = 12
    coupon_likes = 13
    coupon_description = 14
    record_creation_datetime = 15
    record_updation_datetime = 16


def clone_data(coupon_source_website):
    def update(new, old):
        """
        Updates Coupon : hotness, views,

        Parameters
        ----------
        new - new_coupon
        old - old_coupon

        Returns None
        -------

        """

        q = f"UPDATE `final_coupons` SET `coupon_end_date` = '{new[Coupon.coupon_end_date.value]}',`verified_datetime` = '{new[Coupon.verified_datetime.value]}' , `record_updation_datetime` = '{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE `final_coupons`.coupon_id = '{old[Coupon.coupon_id.value]}'"
        cursor.execute(q)
        connection.commit()
        print(f'updated: {old[Coupon.coupon_title.value]}')

    def create(new_coupon):
        '''
        Creates a new coupon in the output database
        Parameters
        ----------
        new_coupon

        Returns
        -------

        '''
        query_1 = f'''INSERT INTO `final_coupons` VALUES('{"', '".join(str(i).replace("'", '"') for i in new_coupon)}')'''
        cursor.execute(query_1)
        connection.commit()
        print(f'created: {new_coupon[Coupon.coupon_title.value]}')

    # code starts

    dt_2hr_before = dt.datetime.now() - dt.timedelta(hours=2)
    dt_2hr_before = dt_2hr_before.strftime('%Y-%m-%d %H:%M:%S')

    # getting last 2hr data

    query = f"SELECT * FROM `coupons_scrapped_data` WHERE coupon_source_website = '{coupon_source_website}' AND (record_creation_datetime >= '{dt_2hr_before}' OR record_updation_datetime >= '{dt_2hr_before}');"
    cursor.execute(query)
    last_2hr_data = cursor.fetchall()

    dt_10days_before = dt.datetime.now() - dt.timedelta(days=10)
    dt_10days_before = dt_10days_before.strftime('%Y-%m-%d %H:%M:%S')

    # querying last 2 hr data with last 10 days data with same coupon code and coupon store
    for coupon in last_2hr_data:
        query_1 = f"SELECT * FROM `final_coupons` WHERE coupon_code = '{coupon[Coupon.coupon_code.value]}' AND coupon_store = '{coupon[Coupon.coupon_store.value]}' AND record_creation_datetime >= '{dt_10days_before}'"
        cursor.execute(query_1)
        coupon_match = cursor.fetchall()
        if len(coupon_match) == 0:
            create(coupon)
        else:
            update(new=coupon, old=coupon_match[0])


# Running the above code

clone_data('desidime')
clone_data('coupondunia')
clone_data('indiafreestuff')
# making cursor to return dictionary
cursor_ = connection.cursor(dictionary=True)
data_list = []
q = 'SELECT * FROM final_coupons'
cursor_.execute(q)
result = cursor_.fetchall()

# outputting to the file
string = json.dumps(result, indent=4, sort_keys=True, default=str)

# writing to a json file
jsonFile = open(f"C:/web_scraping/output_coupons/output_{today}_{time_now}.json", "w")
jsonFile.write(string)
jsonFile.close()


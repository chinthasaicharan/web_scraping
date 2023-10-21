from enum import Enum
import datetime
import urllib
from enum import Enum
from datetime import datetime as dt
from time import sleep
import json
import undetected_chromedriver as uc

# declaring config file
import configparser
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from reused import *


class Coupon(Enum):
    coupon_id = 0
    coupon_title = 1
    coupon_source_website = 2
    coupon_source_url = 3
    coupon_url = 4
    coupon_unique_id = 5
    coupon_code = 6
    coupon_store = 7
    coupon_is_verified = 8
    coupon_verified_datetime = 9
    coupon_is_active = 10
    coupon_start_date = 11
    coupon_end_date = 12
    coupon_success_rate = 13
    coupon_is_code_required = 14
    coupon_users_redeemed = 15
    coupon_likes = 16
    coupon_description = 17
    record_creation_datetime = 18
    record_updation_datetime = 19


column_names = [
    'coupon_title',
    'coupon_source_website',
    'coupon_source_url',
    'coupon_url',
    'coupon_unique_id',
    'coupon_code',
    'coupon_store',
    'coupon_is_verified',
    'coupon_verified_datetime',
    'coupon_is_active',
    'coupon_start_date',
    'coupon_end_date',
    'coupon_success_rate',
    'coupon_is_code_required',
    'coupon_users_redeemed',
    'coupon_likes',
    'coupon_description',
    'record_creation_datetime',
    'record_updation_datetime'
]

config_obj = configparser.ConfigParser()
config_obj.read('config.ini')
PATH = config_obj['driver_path']['PATH']
cursor, connection = load_db(config_obj['main']['DB_NAME'])


def initialize_browser():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if config_obj['coupons']['headless'].lower() == 'yes':
        options.add_argument('--headless')
    browser = webdriver.Chrome(PATH, options=options)
    return browser


def insert_data(coupons_to_insert):
    for row in coupons_to_insert:
        data_str = "\', \'".join(str(i).replace("'", r'\'') for i in row)
        q = f'''INSERT INTO coupons_scrapped_data({', '.join(column_names)}) VALUES('{data_str}')'''
        # # print(q)
        cursor.execute(q)
        connection.commit()
        print(f'Coupon inserted : {row[0]}')


def update_coupon(new, old):
    updated_datetime = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    q = f"UPDATE `coupons_scrapped_data` SET `coupon_users_redeemed` = '{new[-6]}',`coupon_likes` = '{new[-5]}',`coupon_verified_datetime` = '{new[7]}',`record_updation_datetime` = '{updated_datetime}' WHERE `coupon_id` = '{old[Coupon.coupon_id.value]}'"
    cursor.execute(q)
    connection.commit()
    print(f'updated: {old[Coupon.coupon_title.value]}')


def add_update_via_uid(all_coupons, coupons_to_insert: list, ):
    for i in all_coupons:
        query_1 = f"SELECT * FROM `coupons_scrapped_data` WHERE coupon_unique_id = '{i[4]}'"
        cursor.execute(query_1)
        same_deals = cursor.fetchall()
        if len(same_deals) == 0:
            coupons_to_insert.append(i)
        else:
            update_coupon(i, same_deals[0])

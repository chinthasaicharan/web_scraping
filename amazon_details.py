from selenium import webdriver
from bs4 import BeautifulSoup as bs, BeautifulSoup
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt
from time import sleep
from coupons_scraping import Coupon, column_names
from selenium.webdriver.common.by import By

from reused import initImage, clean_link, load_db, reclean_url
import undetected_chromedriver as uc
import html5lib
from coupons_scraping import Coupon
# declaring config file
import configparser

from selectorlib import Extractor
import requests
import json
from time import sleep

browser = webdriver.Chrome('C:/selenium/chromedriver.exe')


# Create an Extractor by reading from the YAML file
def scrape_amazon(url):
    e = Extractor.from_yaml_file('selectors.yml')
    browser.get(url)
    sleep(2)
    data_json = e.extract(browser.page_source)
    print(data_json)
    title = data_json['name']
    desc = data_json['short_description']
    print(title)
    print(desc)


scrape_amazon(
    'https://www.amazon.in/dp/B09N3ZNHTY/ref=s9_acsd_al_bw_c2_x_0_t?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-6&pf_rd_r=PG58DAN8F8VQJ7PW2H2X&pf_rd_t=101&pf_rd_p=2f2eb0c0-0e17-4c14-b29b-146445170845&pf_rd_i=976419031')
browser.quit()

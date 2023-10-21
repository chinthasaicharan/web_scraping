import datetime
import re
from pprint import pprint

from bs4 import BeautifulSoup
from lxml import etree
import requests

# Test url and xpath
URL = "https://www.desidime.com/stores/ajio"
xpath_address = '//*[@id="coupon_411884"]/div/div[2]/div[1]/ul/li[1]/span[2]/time'

response = requests.get(URL)
soup = BeautifulSoup(response.content, "html.parser")
dom = etree.HTML(str(soup))
dtime = dom.xpath(xpath_address)[0].get('datetime')
verified_dt = dtime.split('T')[0] + ' ' + dtime.split('T')[1].split('+')[0]

print(verified_dt)
# expiry_date = dom.xpath(f'//*[@id="coupon_403365"]/div')
expiry_date = dom.xpath(f'//*[@id="coupon_411884"]/div/div[2]/div[1]/ul/li[3]/span[2]')[0].text
users_redeemed = dom.xpath(f'//*[@id="coupon_411884"]/div/div[2]/div[1]/ul/li[2]/span[2]')[0].text
users_redeemed = re.findall(r'-?\d+\.?\d*',users_redeemed)[0]
print(users_redeemed)
# expiry_date = str(expiry_date).strip()
print(expiry_date)
dt_obj = datetime.datetime.strptime(expiry_date[12:].replace('am','AM').replace('pm','PM'),'%B %d, %Y, %H:%M %p')
print(dt_obj)
# code = dom.xpath(f'//*[@id="coupon_{id}"]/div/div[2]/div[2]/div/div[2]')[0].text
c_code = soup.find('a',class_='get_code_tag').find('span',class_='hide-code').text
print(c_code.strip())

#
# all_co = soup.find('div',id='show_coupons_data').find_all('div',class_='coupon_item')
# print(len(all_co))
# pprint(all_co)
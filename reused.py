
import re
from datetime import datetime as dt, timedelta
import urllib.parse


def initImage(path):
    """Initialize path """
    import os
    import shutil
    if not os.path.exists(path):
        os.mkdir(path)


# Text to date
def end_datetime_caliculator(end_date_arr):
    """

    Parameters
    ----------
    Array of text of expire date text

    Returns end_date, end_time from the text
    -------

    """

    end_date = None
    end_time = None

    if 'month' in end_date_arr or 'months' in end_date_arr:
        expiry_date = dt.now() + timedelta(days=30 * int(end_date_arr[-2]))
        end_date = expiry_date.date().strftime('%Y-%m-%d')
        end_time = '23:59:59'
    elif 'day' in end_date_arr or 'days' in end_date_arr:
        expiry_date = dt.now() + timedelta(days=int(end_date_arr[-2]))
        end_date = expiry_date.date().strftime('%Y-%m-%d')
        end_time = '23:59:59'
    elif 'hour' in end_date_arr or 'hours' in end_date_arr:
        expiry_date = dt.now() + timedelta(hours=int(end_date_arr[-2]))
        end_time = expiry_date.time().strftime('%H:%M:%S')
        end_date = expiry_date.date().strftime('%Y-%m-%d')
    return end_date, end_time


# Function for cleaning text
def format_to_text(txt):
    """ Cleans text which has new-line characters"""
    return txt.replace('\n', '')


# Function for returning text from element
def return_text(expression):
    try:
        return format_to_text(expression)
    except:
        return None


# error handling function
def handle_error(exp):
    try:
        return exp
    except Exception as e:
        print(e)
        return None


# Function for cleaning link
def clean_link(link):
    link = urllib.parse.unquote(link)
    # try:
    #     link = link.split('?rto=')[1]
    # except:
    #     pass
    # try:
    #     link = link.split("&url=")[1]
    # except:
    #     pass
    # link = link.split("&affid=")[0]
    # link = link.split("#")[0]
    # link = link.split('?')[0]
    # link = link.split('ref')[0]
    # link = link.split('?m=')[0]
    # return link
    try:
        if link.split('?rto=')[1].startswith('http'):
            link = link.split('?rto=')[1]
        else:
            return link
    except:
        pass
    try:
        link = link.split("&url=")[1]
        if not link.startswith('https'):
            link = 'https://' + link.split('&')[0]
        link = link.split('&')[0]
    except:
        pass
    try:
        link = link.split("?url=")[1]
    except:
        pass
    try:
        link = link.split("&affid=")[0]
    except:
        pass
    try:
        link = link.split("#")[0]
    except:
        pass
    cleaned = link.split('?')
    url_ = cleaned[0]
    # spitting by &
    # e.g : url : https://www.babydove.in/?utm_source=admitad&utm_medium=affiliate&utm_campaign=Baby_Dove_Admitad_cps
    # list = ['utm_source=admitad', 'utm_medium=affiliate', 'utm_campaign=Baby_Dove_Admitad_cps']
    try:
        params_list = cleaned[1].split('&')
    except:
        return url_

    params_to_be_deleted = ['ascsubtag',
                            'affid',
                            'affExtParam1',
                            'affExtParam2',
                            'affExtParam3',
                            'affExtParam4',
                            'affExtParam5',
                            'utm_source',
                            'utm_medium',
                            'utm_campaign',
                            'utm_term',
                            'tagtag_uid']
    # adding allowed tags to a list
    allowed = []
    for key in params_list:
        if key.split('=')[0] not in params_to_be_deleted:
            allowed.append(key)
    # if no allowed params then return only url before ?  otherwise url with normal params
    if len(allowed) != 0:
        return url_ + '?' + '&'.join(allowed)
    if not url_.startswith('http'):
        return 'https://www.' + url_

    return url_


def reclean_url(url):
    if url.startswith('http') or url.startswith('https'):
        store = url.split('/')[2].split('.')[1]
        cleaned_url = url
        if store == 'amazon':
            # finding gp or dp tags
            asin = re.search(r'/[dg]p/([^/]+)', url, flags=re.IGNORECASE)
            if asin:
                asin = asin.group(1)
                asin = asin.split('?')[0]
                cleaned_url = f'https://www.amazon.in/dp/{asin}'
                if cleaned_url.split('/')[4] == 'product':
                    id = url.split('/')[5]
                    cleaned_url = f'https://www.amazon.in/gp/product/{id}'
        return cleaned_url
    return url


# def indiafree_clean(link):
#     if link.split('?rto=')[1]== re.match(pattern=r'^http',string=link):


def load_db(name):
    """
    takes database name as input
    Returns:
        Cursor , Connection if successful
        error if unsuccessful
    """
    import mysql.connector
    db_connection = mysql.connector.connect(
        host='localhost',
        username='root',
        password='',
        database='output'
    )
    print('database connected')
    cursor = db_connection.cursor()
    return cursor, db_connection


def text_to_date(text, date):
    text = text.replace('Expiring In', '')
    text = text.replace('about', '')
    text = text.replace(' ', '')
    date = date.split('-')
    match = re.match(r"([0-9]+)([a-zA-Z]+)", text, re.I)
    if match:
        items = match.groups()
    numeric_val = items[0]
    reference_scale = items[1]
    if (reference_scale == 'months') or (reference_scale == 'month'):
        date[1] = str(int(date[1]) + int(numeric_val))
    elif (reference_scale == 'days') or (reference_scale == 'day'):
        date[2] = str(int(date[2]) + int(numeric_val))
        if int(date[2]) > 30:
            date[2] = int(date[2]) - 30
            date[1] = int(date[1]) + 1
    else:
        pass
    new_date = '-'.join(map(str, date))
    return new_date


def verified_text_to_dt(text):
    text = text.strip()
    text = text.replace('Verified', '')
    if text == '':
        return None


def text_to_expiry_date(text):
    actual = text
    text = text.lower()
    expiry_date = None
    if 'expiring' in text:
        if 'today' in text:
            return dt.today().date().strftime("%Y-%m-%d %H:%M:%S")
        text = text.replace('expiring', '').strip()
        text = text.split(' ')
        numer = int(text[1])
        ref = text[2]
        now = dt.now()
        if ref == 'days':
            expiry_date = now + timedelta(days=numer)
            expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        if ref == 'hours':
            expiry_date = now + timedelta(hours=numer)
        expiry_date = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    elif 'valid' in text:
        for i in ['th', 'nd', 'st', 'rd']:
            actual = actual.replace('Valid till', '').strip().replace(i,'')
        expiry_date = dt.strptime(actual, "%d %b, %y")
    return expiry_date


# print(text_to_expiry_date('Expiring today'))

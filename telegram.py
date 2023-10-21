import json

import requests


def send_telegram_message(alert_type: str,
                          message: str
                          ):
    if alert_type == 'error':
        message = '❌ Error occurred : ' + message
    elif alert_type == 'info':
        message = '✅ Scraping update : ' + message

    headers_ = {'Content-Type': 'application/json',
                'Proxy-Authorization': 'Basic base64'}
    data_dict = {'chat_id': '-1001845377880',
                 'text': message,
                 'parse_mode': 'HTML',
                 'disable_notification': True}
    data = json.dumps(data_dict)
    api_key = '5843855811:AAHBE1Y3XCBVrA6kzGWOSCTN5wMFqiCcQd0'
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    response = requests.post(url,
                             data=data,
                             headers=headers_,
                             verify=False)
    return response

# print(send_telegram_message('error','group chat working ' ))
import requests
from requests.exceptions import ReadTimeout
import time
import telegram
import os

token_devman = os.environ("TOKEN_DEVMAN")
telegram_token = os.environ("TOKEN_BOT")
bot = telegram.Bot(token=telegram_token)
chat_id = os.environ("CHAT_ID")

url = 'https://dvmn.org/api/long_polling/'
headers = {'Authorization': f'Token {token_devman}'}
timeout = 100
request_timestamp = None

while True:
    if request_timestamp == "None":
        params = {"timestamp": time.time()}
    else:
        params = {"timestamp": request_timestamp}
    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        data_json = response.json()
        if data_json['status'] == 'timeout':
            request_timestamp = data_json["timestamp_to_request"]
        if data_json['status'] == 'found':
            lesson_title = data_json['new_attempts'][0]['lesson_title']
            is_negative = data_json['new_attempts'][0]['is_negative']
            lesson_url = "https://dvmn.org" + data_json['new_attempts'][0][
                'lesson_url']
            request_timestamp = data_json['last_attempt_timestamp']
            message_list = [
                f'Преподаватель проверил работу *"{lesson_title}".*'
            ]
            if is_negative:
                message_list.append('К сожалению, в работе есть ошибки. 🙈')
            else:
                message_list.append('Работа принята 🚀')

            message_list.append('\n' + lesson_url)

            message = '\n'.join(message_list)
            bot.send_message(
                chat_id=chat_id, text=message, parse_mode='Markdown')
    except ReadTimeout:
        continue
    except ConnectionError:
        print('Connection Error')

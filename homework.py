import os
import requests
import telegram
import logging
import time
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        data = {'from_date': current_timestamp}
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            params=data,
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        )
        return homework_statuses.json()
    except Exception as e:
        return (f'Ошибка проверки статуса работы: {e}')


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)  # проинициализировать бота здесь
    current_timestamp = 1614608057  # начальное значение timestamp
    logging.debug(f'Запуск бота {current_timestamp}')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]
                    ), bot
                )
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут
        except Exception as e:
            return (f'Бот столкнулся с ошибкой: {e}')
        time.sleep(5)


if __name__ == '__main__':
    main()

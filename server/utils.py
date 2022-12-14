import json
import logging
import random
import string
import time
from pathlib import Path

import httpx
from flask import render_template


BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / 'secrets'
BOT_INFO_URL = 'https://api.twitter.com/2/users/me'


base_formatter = (
    ('-' * 50) + '\n%(asctime)s\n'
    '%(levelname)s:%(name)s\n'
    '%(message)s\n'
)


def error(message: str):
    error = {
        'message': message
    }

    return render_template('index.html', error=error), 400


def merge_params(url: str, params: dict) -> str:
    params_str = '&'.join(map(lambda i: f'{i[0]}={i[1]}', params.items()))
    return url + '?' + params_str


def random_string(lenght=30) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=lenght))


def get_bot_info(token: str) -> dict:
    headers = {'Authorization': f'Bearer {token}'}
    response = httpx.get(BOT_INFO_URL, headers=headers)

    return response.json().get('data', {})


def save_bot_token(data: dict):
    if not isinstance(data, dict) or data.get('access_token') is None:
        raise ValueError('Error to Save Bot Token')

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_in = data['expires_in']

    bot = {
        **get_bot_info(access_token),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': int(time.time() + expires_in),
    }

    with open(SECRETS_DIR / 'bot.json', 'w') as f:
        json.dump(bot, f, indent=4)


def get_logger(name: str, log_file=BASE_DIR / 'server.log', level=logging.WARNING, formatter=base_formatter):
    formatter = logging.Formatter(formatter)

    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

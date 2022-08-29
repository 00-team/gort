
import json
import time

import httpx

from utils import SECRETS_DIR, get_logger, last_retweet


logger = get_logger(__name__)

TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
SEARCH_URL = 'https://api.twitter.com/2/tweets/search/recent'


with open(SECRETS_DIR / 'bot.json') as f:
    BOT_INFO = json.load(f)

with open(SECRETS_DIR / 'keys.json') as f:
    KEYS = json.load(f)


def refresh_token():
    try:
        global BOT_INFO
        headers = {'Authorization': f'Basic {KEYS["BASIC_TOKEN"]}'}

        params = {
            'refresh_token': BOT_INFO['refresh_token'],
            'grant_type': 'refresh_token',
            'client_id': KEYS['CLIENT_ID']
        }

        response = httpx.post(TOKEN_URL, params=params, headers=headers)
        response = response.json()

        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')

        if access_token is None:
            logger.error('access_token is empty')
            logger.error(response)
            exit()

        data = {
            **BOT_INFO,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(time.time() + expires_in),
            'refresh_count': BOT_INFO.get('refresh_count', 0) + 1
        }

        with open(SECRETS_DIR / 'bot.json', 'w') as f:
            json.dump(data, f, indent=4)

        BOT_INFO = data

    except Exception as e:
        logger.exception(e)
        exit()


def get_latest_tweet():
    headers = {'Authorization': f'Bearer {KEYS["BEARER_TOKEN"]}'}
    params = {
        'query': f'#pixelart -from:{BOT_INFO["id"]} -is:retweet',
    }

    # 450 requests per 15-minute
    response = httpx.get(SEARCH_URL, params=params, headers=headers).json()
    return response['data'][0]['id']


def retweet(tweet_id):
    last_rt = last_retweet()

    if last_rt == tweet_id:
        return

    headers = {'Authorization': f'Bearer {BOT_INFO["access_token"]}'}

    url = f'https://api.twitter.com/2/users/{BOT_INFO["id"]}/retweets'

    # 50 requests per 15-minute
    response = httpx.post(url, headers=headers, json={'tweet_id': tweet_id})

    if response.json().get('data', {}).get('retweeted'):
        last_retweet(tweet_id)
    else:
        logger.error(f'{response.status_code}:\n{response.text}')


def main() -> int:
    try:
        if time.time() + 300 > BOT_INFO['expires_in']:
            refresh_token()

        tweet_id = get_latest_tweet()
        retweet(tweet_id)
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    while True:
        status = main()
        time.sleep(67)

import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / 'secrets'


base_formatter = (
    ('-' * 50) + '\n%(asctime)s\n'
    '%(levelname)s:%(name)s\n'
    '%(message)s\n'
)


def get_logger(name: str, log_file=BASE_DIR / 'bot.log', level=logging.WARNING, formatter=base_formatter):
    formatter = logging.Formatter(formatter)

    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def last_retweet(hashtag: str, tweet_id: str | None = None) -> tuple[str | None]:
    hashtag_path = BASE_DIR / f'bot/{hashtag}_last_retweet'
    path = BASE_DIR / f'bot/last_retweet'

    if tweet_id:
        with open(path, 'w') as f:
            f.write(tweet_id)

        with open(hashtag_path, 'w') as f:
            f.write(tweet_id)
    else:
        last_rt, last_hashtag_rt = None, None

        if path.is_file():
            with open(path) as f:
                last_rt = f.read()

        if hashtag_path.is_file():
            with open(hashtag_path) as f:
                last_hashtag_rt = f.read()

        return last_rt, last_hashtag_rt

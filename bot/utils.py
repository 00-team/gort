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


def last_retweet(tweet_id: str | None = None) -> str | None:
    path = BASE_DIR / 'bot/last_retweet'

    if tweet_id:
        with open(path, 'w') as f:
            f.write(tweet_id)
    else:
        if not path.is_file():
            return

        with open(path) as f:
            return f.read()

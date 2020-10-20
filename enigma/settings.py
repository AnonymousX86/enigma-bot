from os import environ

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get(thing: str):
    return environ.get(thing)


def in_dev() -> bool:
    return str(get('TARGET')) == 'development'


def in_production() -> bool:
    return not in_dev()


version = '0.2'


general_settings = {
    'bot_token': str(get('BOT_TOKEN')),
    'owner_id': int(get('OWNER_ID')),
}

database_settings = {
    'url': str(get('DATABASE_URL')),
    'user': str(get('DB_USER')),
    'password': str(get('DB_PASSWORD')),
    'host': str(get('DB_HOST')),
    'port': str(get('DB_PORT')),
    'database': str(get('DB_DATABASE'))
}

debug_settings = {
    'channel': int(get('DEBUG_CHANNEL')),
}

reddit_settings = {
    'client_id': get('REDDIT_CLIENT_ID'),
    'client_secret': get('REDDIT_SECRET'),
    'user_agent': get('REDDIT_USER_AGENT')
}

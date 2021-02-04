from os import environ

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def _get(thing: str) -> str:
    return str(environ.get(thing))


def in_dev() -> bool:
    return str(_get('TARGET')) == 'development'


def in_production() -> bool:
    return not in_dev()


def version() -> str:
    return '0.6'


general_settings = {
    'bot_token': _get('BOT_TOKEN'),
    'owner_id': int(_get('OWNER_ID')),
    'suggestions_channel': int(_get('SUGGESTION_CHANNEL'))
}

database_settings = {
    'url': _get('DATABASE_URL'),
    'user': _get('DB_USER'),
    'password': _get('DB_PASSWORD'),
    'host': _get('DB_HOST'),
    'port': _get('DB_PORT'),
    'database': _get('DB_DATABASE')
}

debug_settings = {
    'channel': int(_get('DEBUG_CHANNEL')),
}

reddit_settings = {
    'client_id': _get('REDDIT_CLIENT_ID'),
    'client_secret': _get('REDDIT_SECRET'),
    'user_agent': _get('REDDIT_USER_AGENT')
}

rapidapi_settings = {
    'key': _get('RAPIDAPI_KEY')
}

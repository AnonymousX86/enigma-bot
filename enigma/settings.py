import os
from ast import literal_eval

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get(thing: str):
    return os.environ.get(thing)


general_settings = {
    'bot_token': str(get('BOT_TOKEN')),
    'owner_id': int(get('OWNER_ID')),
}

database_settings = {
    'full_url': str(get('DB_URL')),
    'user': str(get('DB_USER')),
    'password': str(get('DB_PASSWORD')),
    'host': str(get('DB_HOST')),
    'port': str(get('DB_PORT')),
    'database': str(get('DB_DATABASE'))
}

cache_settings = {
    'servers': literal_eval(f"['{get('CACHE_SERVERS')}']"),
    'user': str(get('CACHE_USER')),
    'password': str(get('CACHE_PASSWORD')),
}

debug_settings = {
    'channel': int(get('DEBUG_CHANNEL')),
}

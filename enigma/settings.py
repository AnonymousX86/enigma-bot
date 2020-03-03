import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BOT_TOKEN: str = os.environ.get('BOT_TOKEN')
OWNER_ID: int = os.environ.get('OWNER_ID')

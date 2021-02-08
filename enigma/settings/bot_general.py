# -*- coding: utf-8 -*-
from os import environ as env


def in_production() -> bool:
    return env.get('TARGET') == 'production'


def bot_token() -> str:
    return env.get('BOT_TOKEN')


def bot_version() -> str:
    return '0.6'


def bot_owner_id() -> int:
    return 309270832683679745

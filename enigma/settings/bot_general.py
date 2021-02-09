# -*- coding: utf-8 -*-
from os import environ as env


def environment() -> str:
    return env.get('TARGET')


def in_production() -> bool:
    return environment() == 'production'


def bot_token() -> str:
    return env.get('BOT_TOKEN')


def bot_version() -> str:
    return '0.7'


def bot_owner_id() -> int:
    return 309270832683679745

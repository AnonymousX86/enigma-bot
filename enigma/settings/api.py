# -*- coding: utf-8 -*-
from os import environ as env

from enigma.settings.bot_general import bot_version


def reddit_client_id() -> str:
    return env.get('REDDIT_CLIENT_ID')


def reddit_client_secret() -> str:
    return env.get('REDDIT_SECRET')


def reddit_user_agent() -> str:
    return env.get('REDDIT_USER_AGENT').format(bot_version())


def rapid_api_key() -> str:
    return env.get('RAPIDAPI_KEY')


def spotify_client_id() -> str:
    return env.get('SPOTIFY_CLIENT_ID')


def spotify_client_secret() -> str:
    return env.get('SPOTIFY_CLIENT_SECRET')

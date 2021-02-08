# -*- coding: utf-8 -*-
from os import environ as env


def debug_channel_id() -> int:
    return int(env.get('DEBUG_CHANNEL'))


def suggestions_channel_id() -> int:
    return int(env.get('SUGGESTION_CHANNEL'))


def system_channel_id() -> int:
    return int(env.get('SYSTEM_CHANNEL'))

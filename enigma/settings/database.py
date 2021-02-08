# -*- coding: utf-8 -*-
from os import environ as env


def database_url() -> str:
    return env.get('DATABASE_URL')

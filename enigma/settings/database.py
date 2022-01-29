# -*- coding: utf-8 -*-
from os import environ as env


def database_url() -> str:
    url = env.get('DATABASE_URL')
    if not url:
        raise RuntimeError("No database url found")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://")
    return url

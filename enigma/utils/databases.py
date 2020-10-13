import bmemcached
import psycopg2

from ..settings import database_settings, cache_settings


def postgre_connect() -> psycopg2.connect:
    """Connect to PostgreSQL database"""
    conn = psycopg2.connect(
        user=database_settings['user'],
        password=database_settings['password'],
        host=database_settings['host'],
        port=database_settings['port'],
        database=database_settings['database'],
        sslmode='require'
    )
    return conn


def cache_client() -> bmemcached.Client:
    """Return connection to cache server object"""
    servers = cache_settings['servers']
    user = cache_settings['user']
    password = cache_settings['password']
    mc = bmemcached.Client(servers, username=user, password=password)
    mc.enable_retry_delay(True)
    return mc


def query_all_users() -> list:
    """Return all columns from 'users' table"""
    db = postgre_connect()
    c = db.cursor()
    c.execute('SELECT * FROM users;')
    result: list = c.fetchall()
    c.close()
    db.close()
    return result


def query_single_user(user_id: int) -> list:
    """Find if there's user in database"""
    db = postgre_connect()
    c = db.cursor()
    c.execute(
        'SELECT * FROM users WHERE user_id = %s::bigint',
        (
            user_id,
        )
    )
    result: list = c.fetchall()
    c.close()
    db.close()
    return result

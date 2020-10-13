import bmemcached
import psycopg2

from ..settings import database_settings, cache_settings


def postgre_connect() -> psycopg2.connect:
    """
    Connects to PostgreSQL database.

    :return: Connection object.
    """
    conn = psycopg2.connect(
        # user=database_settings['user'],
        # password=database_settings['password'],
        # host=database_settings['host'],
        # port=database_settings['port'],
        # database=database_settings['database'],
        database_settings['url'],
        sslmode='require'
    )
    return conn


def cache_client() -> bmemcached.Client:
    """
    Connects to cache server.

    :return: Connection object.
    """
    servers = cache_settings['servers']
    user = cache_settings['user']
    password = cache_settings['password']
    mc = bmemcached.Client(servers, username=user, password=password)
    mc.enable_retry_delay(True)
    return mc


def query_all_users() -> list:
    """
    Gets all users' data from database.

    :return: All users' data.
    """
    db = postgre_connect()
    c = db.cursor()
    c.execute('SELECT * FROM users;')
    result: list = c.fetchall()
    c.close()
    db.close()
    return result


def query_single_user(user_id: int) -> list:
    """
    Gets single user's data from database.

    :param user_id: User ID.
    :return: Single user's data.
    """
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

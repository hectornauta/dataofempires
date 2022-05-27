from decouple import config

import redis

REDIS_HOST = config('REDIS_HOST')
REDIS_USER = config('REDIS_USER')
REDIS_PORT = config('REDIS_PORT')
REDIS_PASS = config('REDIS_PASS')
REDIS_URI = config('REDIS_URI')

import logging_config

logger = logging_config.configure_logging('redis_functions')

def create_connection():
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USER, password=REDIS_PASS, ssl=True, ssl_cert_reqs=None)
    return conn

def load_dict(my_hash, my_dict):
    conn = create_connection()
    conn.hmset(my_hash, my_dict)

def get_dict(my_hash):
    conn = create_connection()
    conn.hgetall(my_hash)

def get_profile_id_by_name(name):
    conn = create_connection()
    profile_id = conn.hget('names', name)
    logger.info(profile_id)
    if profile_id is None:
        return None
    else:
        return profile_id.decode('utf-8')

def get_profile_id_by_steam_id(steam_id):
    conn = create_connection()
    profile_id = conn.hget('steam_ids', steam_id)
    logger.info(profile_id)
    return profile_id
def get_all():
    conn = create_connection()
    # logger.info(conn.hgetall('steam_ids'))
    logger.info(conn.hgetall('names'))

def pingpong():
    conn = create_connection()
    logger.info(conn)
    conn.ping()
if __name__ == "__main__":
    get_profile_id_by_name('Hectornauta')
    get_profile_id_by_steam_id(76561198147771075)

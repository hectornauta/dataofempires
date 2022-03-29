import pandas as pd
import logging
import os

from decouple import config

import numpy as np
import sqlalchemy as db
from sqlalchemy import exc
from sqlalchemy.types import Float
from sqlalchemy.types import String
from sqlalchemy.types import SmallInteger

from sqlalchemy.sql import select
from sqlalchemy import MetaData
from sqlalchemy import Table

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')

DIR = os.path.dirname(__file__)

def get_sql_results(query_file, ladder=-1, min_elo=-1, max_elo=-1):
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        with open(query_file, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    else:
        if ladder != -1 and min_elo == -1 and max_elo == -1:
            dataframe_results = pd.read_sql_query(sql_query, sql_connection, params={'ladder': ladder})
        elif ladder == -1 or min_elo == 1 or max_elo == -1:
            dataframe_results = pd.read_sql_query(sql_query, sql_connection)
        else:
            dataframe_results = pd.read_sql_query(sql_query, sql_connection, params={'ladder': ladder, 'min_elo': min_elo, 'max_elo': max_elo})
        return dataframe_results
def get_sql_matches_players(ladder=-1, min_elo=-1, max_elo=-1, num_players=-1):
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    engine = db.create_engine(sql_connection)
    conn = engine.connect()
    matches_metadata = MetaData()
    matches = Table('matches', matches_metadata, autoload_with=engine)
    matches_query = select(matches)
    results = conn.execute(matches_query)
    logger.info(matches)
    logger.info(matches_metadata)
    logger.info(matches_query)
    for result in results:
        logger.info(result)

def get_civ_vs_civ():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    engine = db.create_engine(sql_connection)
    conn = engine.connect()
    civ_vs_civ_metadata = MetaData()
    civ_vs_civ_table = Table('civ_vs_civ', civ_vs_civ_metadata, autoload_with=engine)
    civ_vs_civ_query = select(civ_vs_civ_table)
    results = conn.execute(civ_vs_civ_query)
    return results
if __name__ == "__main__":
    get_civ_vs_civ()
    logger.info('...')

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

def get_sql_results(query_file):
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        with open(query_file, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    else:
        dataframe_results = pd.read_sql_query(sql_query, sql_connection)
        return dataframe_results

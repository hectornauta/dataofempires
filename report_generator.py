import logging
import os

from decouple import config

import numpy as np
import pandas as pd
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

CIVS = pd.read_csv('csv/civs.csv')
CIVS.drop(['numero'], axis=1, inplace=True)
CIVS.set_index('id', inplace=True)

DIR = os.path.dirname(__file__)

def best_civs_duo():
    # Probar con GROUP BY match + team
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_all_duo_matches.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_matches_players = pd.read_sql_query(sql_query, sql_connection)
    number_of_matches = int(len(dataframe_matches_players) / 4)
    dataframe_matches_players = dataframe_matches_players.drop(['rating', 'map_type', 'country'], axis=1)
    dataframe_matches_players = dataframe_matches_players.merge(dataframe_matches_players, how='left', left_on=['match_id', 'team'], right_on=['match_id', 'team'])
    # logger.info(f'\n {dataframe_matches_players}')
    dataframe_matches_players = dataframe_matches_players[dataframe_matches_players['slot_x'] != dataframe_matches_players['slot_y']]
    dataframe_matches_players = dataframe_matches_players[dataframe_matches_players['slot_x'] < 3]
    dataframe_matches_players['lost'] = ~dataframe_matches_players['won_x']
    c = ['civ_x', 'civ_y']
    df1 = dataframe_matches_players.groupby(np.sort(dataframe_matches_players[c], axis=1).T.tolist())['won_x'].sum()
    df2 = dataframe_matches_players.groupby(np.sort(dataframe_matches_players[c], axis=1).T.tolist())['lost'].sum()
    df4 = dataframe_matches_players.groupby(np.sort(dataframe_matches_players[c], axis=1).T.tolist()).size()
    df3 = df1 + df2
    df3 = df3.sort_values()
    # logger.info(f'\n {dataframe_matches_players}')
    # dataframe_matches_players = dataframe_matches_players.groupby(['civ_x', 'civ_y']).agg(
    #     number_of_wins=pd.NamedAgg(column="won_x", aggfunc="count")
    # )
    # dataframe_matches_players = dataframe_matches_players.reset_index()
    # dataframe_matches_players = dataframe_matches_players[~pd.DataFrame(np.sort(dataframe_matches_players.filter(like='civ_'))).duplicated()]
    # dataframe_matches_players = dataframe_matches_players.sort_values(by=['number_of_wins'])
    logger.info(f'\n {dataframe_matches_players}')
    logger.info(f'\n {df1}')
    logger.info(f'\n {df2}')
    logger.info(f'\n {df3}')
    logger.info(f'\n {df4}')


def civ_winrate():
    # Obtiene los rates del RM 1vs1
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_all_normal_matches.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_matches_players = pd.read_sql_query(sql_query, sql_connection)
    number_of_matches = int(len(dataframe_matches_players) / 2)
    # logger.info(dataframe_matches_players)
    dataframe_civ_rates = CIVS.copy()
    dataframe_civ_rates = dataframe_civ_rates.reset_index()
    dataframe_civ_rates['number_of_wins'] = 0
    # logger.info(dataframe_civ_rates)
    dataframe_civ_rates = dataframe_civ_rates.merge(dataframe_matches_players, left_on='id', right_on='civ')
    # logger.info(dataframe_civ_rates)
    dataframe_civ_rates = dataframe_civ_rates.groupby(['id', 'name', 'nombre']).agg(
        number_of_wins=pd.NamedAgg(column="won", aggfunc="sum"),
        number_of_picks=pd.NamedAgg(column="id", aggfunc="count"))
    dataframe_civ_rates['winrate'] = (dataframe_civ_rates['number_of_wins'] / dataframe_civ_rates['number_of_picks'])
    dataframe_civ_rates['pickrate'] = (dataframe_civ_rates['number_of_picks'] / number_of_matches)
    dataframe_civ_rates = dataframe_civ_rates.drop(['number_of_picks', 'number_of_wins'], axis=1)
    # logger.info(dataframe_civ_rates)

    engine = db.create_engine(sql_connection)
    try:
        dataframe_civ_rates.to_sql(
            'civ_rates',
            con=engine.connect(),
            if_exists='replace',
            index=True,
            dtype={
                'id': SmallInteger(),
                'name': String(),
                'nombre': String(),
                'winrate': Float(),
                'pickrate': Float()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    finally:
        logger.info('Cargados los reportes')

if __name__ == "__main__":
    best_civs_duo()

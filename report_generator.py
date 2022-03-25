import logging
import os

from decouple import config

import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy import exc
from sqlalchemy.types import Float
from sqlalchemy.types import String
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger

import sql_functions

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

def add_combination(dict_civs, civ_1, civ_2, won_1):
    first_comb = (civ_1, civ_2)
    second_comb = (civ_2, civ_1)
    if first_comb in dict_civs:
        dict_civs[first_comb][0] = dict_civs[first_comb][0] + int(won_1)
        dict_civs[first_comb][1] = dict_civs[first_comb][1] + 1
    else:
        dict_civs[first_comb] = [int(won_1), 1, civ_1, civ_2]
    if second_comb in dict_civs:
        dict_civs[second_comb][0] = dict_civs[second_comb][0] + int(not won_1)
        dict_civs[second_comb][1] = dict_civs[second_comb][1] + 1
    else:
        dict_civs[second_comb] = [int(not won_1), 1, civ_2, civ_1]


def civ_vs_civ():
    FILE = f'{DIR}/sql/get_all_1vs1_matches.sql'
    dataframe_matches_players = sql_functions.get_sql_results(FILE)
    dataframe_matches_players = dataframe_matches_players.drop(['rating', 'country'], axis=1)
    dataframe_matches_players = dataframe_matches_players.merge(dataframe_matches_players, how='inner', left_on=['match_id'], right_on=['match_id'])
    dataframe_matches_players = dataframe_matches_players[dataframe_matches_players['civ_x'] != dataframe_matches_players['civ_y']]
    dataframe_matches_players = dataframe_matches_players[dataframe_matches_players['slot_x'] < 2]
    dict_civ_vs_civ = dataframe_matches_players.to_dict('records')
    DICT_CIVS = {}
    for match in dict_civ_vs_civ:
        add_combination(DICT_CIVS, match['civ_x'], match['civ_y'], match['won_x'])
    dataframe_civ_vs_civ = pd.DataFrame.from_dict(DICT_CIVS, orient='index', columns=['wins', 'matches', 'civ_1', 'civ_2'])
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.reset_index()
    dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['wins'] / dataframe_civ_vs_civ['matches']
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.drop(['index'], axis=1)
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.sort_values(by='winrate', ascending=False)
    logger.info(dataframe_civ_vs_civ)

    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        dataframe_civ_vs_civ.to_sql(
            'civ_vs_civ',
            con=engine.connect(),
            if_exists='replace',
            index=True,
            dtype={
                'civ_1': SmallInteger(),
                'civ_2': SmallInteger(),
                'wins': Integer(),
                'matches': Integer(),
                'winrate': Float()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los reportes de civ vs civ')

def best_civs_duo():
    FILE = f'{DIR}/sql/get_all_duo_matches.sql'
    dataframe_matches_players = sql_functions.get_sql_results(FILE)
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
    FILE = f'{DIR}/sql/get_all_1vs1_matches.sql'
    dataframe_matches_players = sql_functions.get_sql_results(FILE)
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

    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
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
    else:
        logger.info('Cargados los reportes de civ rates')

if __name__ == "__main__":
    civ_vs_civ()

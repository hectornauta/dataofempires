import logging
import os

from decouple import config

from functools import reduce

import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy import exc
from sqlalchemy.types import Float
from sqlalchemy.types import String
from sqlalchemy.types import Integer
from sqlalchemy.types import BigInteger
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import NCHAR

import sql_functions

import gamedata

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

MAPS = pd.read_csv('csv/maps.csv', sep=';')
MAPS.set_index('id', inplace=True)

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

def country_elo():
    COUNTRIES = gamedata.countries()
    FILE_QUERY = f'{DIR}/sql/get_ranked_matches_ladder.sql'

    labels = [
        '3',
        '4',
        '13',
        '14'
    ]
    dict_iterations = {
        1: '3',
        2: '4',
        3: '13',
        4: '14',
    }

    dataframe_rm_solo = sql_functions.get_sql_results(FILE_QUERY, 3)
    dataframe_rm_solo = dataframe_rm_solo.reset_index()
    dataframe_rm_team = sql_functions.get_sql_results(FILE_QUERY, 4)
    dataframe_rm_team = dataframe_rm_team.reset_index()
    dataframe_ew_solo = sql_functions.get_sql_results(FILE_QUERY, 13)
    dataframe_ew_solo = dataframe_ew_solo.reset_index()
    dataframe_ew_team = sql_functions.get_sql_results(FILE_QUERY, 14)
    dataframe_ew_team = dataframe_ew_team.reset_index()
    all_dataframes = [
        dataframe_rm_solo,
        dataframe_rm_team,
        dataframe_ew_solo,
        dataframe_ew_team
    ]
    all_countries_dataframes = []
    iteration = 0
    for dataframe in all_dataframes:
        iteration = iteration + 1
        dataframe = dataframe.sort_values('finished')
        dataframe = dataframe.groupby(['country', 'profile_id']).agg(
            rating=pd.NamedAgg(column="rating", aggfunc="last")
        )
        dataframe = dataframe.reset_index()
        dataframe = dataframe.groupby(['country']).agg(
            number_of_players=pd.NamedAgg(column="profile_id", aggfunc="count"),
            mean_elo=pd.NamedAgg(column="rating", aggfunc="mean"),
            max_elo=pd.NamedAgg(column="rating", aggfunc="max"),
            # std_elo=pd.NamedAgg(column="rating", aggfunc="std"),
            # sem_elo=pd.NamedAgg(column="rating", aggfunc="sem"),
            # var_elo=pd.NamedAgg(column="rating", aggfunc="var")
        )
        dataframe = dataframe.rename(
            columns={
                'number_of_players': f'number_of_players_{dict_iterations[iteration]}',
                'mean_elo': f'mean_elo_{dict_iterations[iteration]}',
                'max_elo': f'max_elo_{dict_iterations[iteration]}'
            }
        )
        all_countries_dataframes.append(dataframe)
    
    dataframe_final = reduce(lambda df1, df2: pd.merge(df1, df2, how='outer', on=['country']), all_countries_dataframes)
    # logger.info(dataframe_final)
    dataframe_final = dataframe_final.rename(
        columns={
            'number_of_players_': f'number_of_players__{dict_iterations[iteration]}',
            'mean_elo': f'mean_elo_{dict_iterations[iteration]}',
            'max_elo': f'max_elo_{dict_iterations[iteration]}'
        }
    )
    dataframe_final = dataframe_final.sort_values(by=['country'])
    # logger.info(dataframe_final)
    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        dataframe_final.to_sql(
            'countries_elo',
            con=engine.connect(),
            if_exists='replace',
            index=True,
            dtype={
                'country': NCHAR(2)
            }
        )
    except exc.SQLAlchemyError:
        logger.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los reportes de países')
    return None

def map_playrate():
    FILE = f'{DIR}/sql/get_all_1vs1_matches.sql'
    dataframe_maps_rates = sql_functions.get_sql_results(FILE)
    dataframe_maps_rates = dataframe_maps_rates.drop(['rating', 'country', 'won', 'civ'], axis=1)
    dataframe_maps_rates = dataframe_maps_rates[dataframe_maps_rates['slot'] == 1]
    dataframe_maps = MAPS.copy()
    dataframe_maps = dataframe_maps.reset_index()
    # logger.info(dataframe_maps_rates)
    # logger.info(dataframe_maps)
    dataframe_maps_rates = dataframe_maps_rates.merge(dataframe_maps, left_on='map_type', right_on='id')
    total_matches = len(dataframe_maps_rates)
    # logger.info(total_matches)

    dataframe_maps_rates = dataframe_maps_rates.groupby(['id']).agg(
        number_of_matches=pd.NamedAgg(column="id", aggfunc="count")
    )
    dataframe_maps_rates['playrate'] = dataframe_maps_rates['number_of_matches'] / total_matches
    dataframe_maps_rates = dataframe_maps_rates.sort_values(by='playrate', ascending=False)
    dataframe_maps_rates = dataframe_maps_rates.reset_index()
    dataframe_maps_rates = dataframe_maps_rates.merge(dataframe_maps, left_on='id', right_on='id')
    # logger.info(dataframe_maps_rates)

    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        dataframe_maps_rates.to_sql(
            'maps_playrate',
            con=engine.connect(),
            if_exists='replace',
            index=False,
            dtype={
                'id': SmallInteger(),
                'number_of_matches': Integer(),
                'playrate': Float(),
                'name': String(),
                'nombre': String()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los reportes de mapas')

def civ_vs_civ():
    FILE_SOLO = f'{DIR}/sql/get_ranked_matches_params.sql'

    dataframe_civ = gamedata.civs()
    dataframe_civ = dataframe_civ.reset_index()
    labels = [
        '3A', '3B', '3C',
        '13A', '13B'
    ]
    dict_iterations = {
        1: '3A',
        2: '3B',
        3: '3C',
        4: '13A',
        5: '13B'
    }
    dataframe_rm_solo_a = sql_functions.get_sql_results(FILE_SOLO, 3, 1000, 1300)
    dataframe_rm_solo_a = dataframe_rm_solo_a.reset_index()
    dataframe_rm_solo_b = sql_functions.get_sql_results(FILE_SOLO, 3, 1300, 1600)
    dataframe_rm_solo_b = dataframe_rm_solo_b.reset_index()
    dataframe_rm_solo_c = sql_functions.get_sql_results(FILE_SOLO, 3, 1600, 2500)
    dataframe_rm_solo_c = dataframe_rm_solo_c.reset_index()
    dataframe_ew_solo_a = sql_functions.get_sql_results(FILE_SOLO, 13, 900, 1200)
    dataframe_ew_solo_a = dataframe_ew_solo_a.reset_index()
    dataframe_ew_solo_b = sql_functions.get_sql_results(FILE_SOLO, 13, 1200, 2000)
    dataframe_ew_solo_b = dataframe_ew_solo_b.reset_index()
    all_dataframes = [
        dataframe_rm_solo_a, dataframe_rm_solo_b, dataframe_rm_solo_c,
        dataframe_ew_solo_a, dataframe_ew_solo_b
    ]
    all_civ_vs_civ_dataframes = []
    iteration = 0
    for dataframe in all_dataframes:
        iteration = iteration + 1
        dataframe = dataframe.drop(['rating', 'country'], axis=1)
        dataframe = dataframe.merge(dataframe, how='inner', left_on=['match_id'], right_on=['match_id'])
        dataframe = dataframe[dataframe['civ_x'] != dataframe['civ_y']]
        dataframe = dataframe[dataframe['slot_x'] < 2]
        dataframe_temp = dataframe.to_dict('records')
        DICT_CIVS = {}
        for match in dataframe_temp:
            add_combination(DICT_CIVS, match['civ_x'], match['civ_y'], match['won_x'])
        dataframe_temp = pd.DataFrame.from_dict(DICT_CIVS, orient='index', columns=['wins', 'matches', 'civ_1', 'civ_2'])
        dataframe_temp = dataframe_temp.reset_index()
        dataframe_temp['winrate'] = dataframe_temp['wins'] / dataframe_temp['matches']
        dataframe_temp = dataframe_temp.drop(['index'], axis=1)
        dataframe_temp = dataframe_temp.sort_values(by='winrate', ascending=False)
        dataframe_temp = dataframe_temp.set_index(['civ_1', 'civ_2'])

        dataframe_temp = dataframe_temp.rename(
            columns={
                'winrate': f'winrate_{dict_iterations[iteration]}',
                'matches': f'matches_{dict_iterations[iteration]}',
                'wins': f'wins_{dict_iterations[iteration]}'
            }
        )
        all_civ_vs_civ_dataframes.append(dataframe_temp)
    # for dataframe in all_civ_vs_civ_dataframes:
        # logger.info(f'{dataframe.index}')
        # logger.info(f'\n {dataframe}')
    dataframe_final = reduce(lambda df1, df2: pd.merge(df1, df2, how='outer', on=['civ_1', 'civ_2']), all_civ_vs_civ_dataframes)
    dataframe_final = dataframe_final.rename(
        columns={
            'winrate': f'winrate_{dict_iterations[iteration]}',
            'matches': f'matches_{dict_iterations[iteration]}',
            'wins': f'wins_{dict_iterations[iteration]}'
        }
    )
    dataframe_final = dataframe_final.sort_values(by=['civ_1', 'civ_2'])
    # logger.info(f'{dataframe_final}')
    iteration = 0
    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        dataframe_final.to_sql(
            'civ_vs_civ',
            con=engine.connect(),
            if_exists='replace',
            index=True,
            dtype={
                'civ_1': SmallInteger(),
                'civ_2': SmallInteger()
                # 'wins': Integer(),
                # 'matches': Integer(),
                # 'winrate': Float(),
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los reportes de civ vs civ')

    '''
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
    logger.info(f'\n {dataframe_civ_vs_civ}')
    '''


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
    # logger.info(f'\n {dataframe_matches_players}')
    # logger.info(f'\n {df1}')
    # logger.info(f'\n {df2}')
    # logger.info(f'\n {df3}')
    # logger.info(f'\n {df4}')


def civ_rates():
    FILE_SOLO = f'{DIR}/sql/get_ranked_matches_params.sql'
    FILE_TEAM = f'{DIR}/sql/get_ranked_matches_team_params.sql'
    dataframe_civ = CIVS.copy()
    dataframe_civ = dataframe_civ.reset_index()
    labels = [
        '3A', '3B', '3C',
        '4A', '4B', '4C',
        '13A', '13B',
        '14A', '14B'
    ]
    dataframe_rm_solo_a = sql_functions.get_sql_results(FILE_SOLO, 3, 1000, 1300)
    dataframe_rm_solo_a = dataframe_rm_solo_a.reset_index()
    dataframe_rm_solo_b = sql_functions.get_sql_results(FILE_SOLO, 3, 1300, 1600)
    dataframe_rm_solo_b = dataframe_rm_solo_b.reset_index()
    dataframe_rm_solo_c = sql_functions.get_sql_results(FILE_SOLO, 3, 1600, 2500)
    dataframe_rm_solo_c = dataframe_rm_solo_c.reset_index()
    dataframe_rm_team_a = sql_functions.get_sql_results(FILE_TEAM, 4, 1000, 1600)
    dataframe_rm_team_a = dataframe_rm_team_a.reset_index()
    dataframe_rm_team_b = sql_functions.get_sql_results(FILE_TEAM, 4, 1600, 2200)
    dataframe_rm_team_b = dataframe_rm_team_b.reset_index()
    dataframe_rm_team_c = sql_functions.get_sql_results(FILE_TEAM, 4, 2200, 3500)
    dataframe_rm_team_c = dataframe_rm_team_c.reset_index()
    dataframe_ew_solo_a = sql_functions.get_sql_results(FILE_SOLO, 13, 900, 1200)
    dataframe_ew_solo_a = dataframe_ew_solo_a.reset_index()
    dataframe_ew_solo_b = sql_functions.get_sql_results(FILE_SOLO, 13, 1200, 2000)
    dataframe_ew_solo_b = dataframe_ew_solo_b.reset_index()
    dataframe_ew_team_a = sql_functions.get_sql_results(FILE_TEAM, 14, 900, 1300)
    dataframe_ew_team_a = dataframe_ew_team_a.reset_index()
    dataframe_ew_team_b = sql_functions.get_sql_results(FILE_TEAM, 14, 1300, 2000)
    dataframe_ew_team_b = dataframe_ew_team_b.reset_index()
    all_dataframes = [
        dataframe_rm_solo_a, dataframe_rm_solo_b, dataframe_rm_solo_c,
        dataframe_rm_team_a, dataframe_rm_team_b, dataframe_rm_team_c,
        dataframe_ew_solo_a, dataframe_ew_solo_b,
        dataframe_ew_team_a, dataframe_ew_team_b
    ]
    iteration = 0
    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    for index, dataframe in enumerate(all_dataframes):
        number_of_matches = all_dataframes[index]['match_id'].nunique()
        all_dataframes[index]['number_of_wins'] = 0
        all_dataframes[index] = dataframe_civ.merge(all_dataframes[index], left_on='id', right_on='civ')
        all_dataframes[index] = all_dataframes[index].groupby(['id', 'name', 'nombre']).agg(
            number_of_wins=pd.NamedAgg(column="won", aggfunc="sum"),
            number_of_picks=pd.NamedAgg(column="id", aggfunc="count"))
        all_dataframes[index]['winrate'] = (all_dataframes[index]['number_of_wins'] / all_dataframes[index]['number_of_picks'])
        all_dataframes[index]['pickrate'] = (all_dataframes[index]['number_of_picks'] / number_of_matches)
        all_dataframes[index] = all_dataframes[index].drop(['number_of_picks', 'number_of_wins'], axis=1)
        all_dataframes[index]['ladder_cat'] = labels[iteration]
        if iteration == 0:
            condition = 'replace'
        else:
            condition = 'append'
        try:
            all_dataframes[index].to_sql(
                'civ_rates',
                con=engine.connect(),
                if_exists=condition,
                index=True,
                dtype={
                    'id': SmallInteger(),
                    'name': String(),
                    'nombre': String(),
                    'winrate': Float(),
                    'pickrate': Float(),
                    'label': String()
                }
            )
        except exc.SQLAlchemyError:
            logging.error('Error en la conexión a la base de datos')
            raise Exception('Error al conectar a la base de datos')
        else:
            logger.info(f'Cargados los reportes de civ rates para {labels[iteration]}')
        iteration = iteration + 1

def update_players_elo():
    FILE = f'{DIR}/sql/get_players_info.sql'
    dataframe_players_info = sql_functions.get_sql_results(FILE)
    dataframe_players_info = dataframe_players_info.groupby(['profile_id', 'steam_id', 'name', 'country'], sort=False)['finished'].max()
    dataframe_players_info = dataframe_players_info.reset_index()
    dataframe_players_info.to_json(path_or_buf='json/players.json', orient="records")
    engine = db.create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    try:
        dataframe_players_info.to_sql(
            'players',
            con=engine.connect(),
            if_exists='replace',
            index=False,
            dtype={
                'profile_id': Integer(),
                'steam_id': BigInteger(),
                'name': VARCHAR(32),
                'country': NCHAR(2),
                'finished': Integer()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Actualizados los players')

def update_all():
    best_civs_duo()
    civ_vs_civ()
    civ_rates()
    map_playrate()
    country_elo()
    update_players_elo()

if __name__ == "__main__":
    ALL = False
    if ALL:
        update_all()
    else:
        country_elo()

import json
import logging
import requests
import time


import psycopg2
from decouple import config

import pandas as pd
import sqlalchemy as db
from datetime import datetime, timedelta
from math import trunc

from sqlalchemy import exc
from sqlalchemy.types import Integer
from sqlalchemy.types import Boolean
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import String
from sqlalchemy.types import BigInteger
from sqlalchemy.types import NCHAR

import query_functions

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

def get_last_match():
    # Conexión con BD
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    engine = db.create_engine(sql_connection)
    with engine.connect() as con:
        try:
            last_match = con.execute('SELECT match_id FROM matches ORDER BY match_id DESC LIMIT 1')
        except (psycopg2.DatabaseError) as error:
            logger.error(error)
            logger.error('Error al obtener el último match')
            raise Exception('Error al obtener el último match')
        except db.exc.ProgrammingError as error:
            last_match = 0
        else:
            # logger.info(last_match)
            last_match = last_match.first()[0]
            logger.info(last_match)
    # last_match = 140063221
    return last_match

def extract_matches(param_timestamp, session):
    logger.info('Realizando request')
    number_of_matches = 1000
    timestamp = param_timestamp
    query = query_functions.get_matches(number_of_matches, timestamp)
    logger.info(f'Query creada: {query}')
    try:
        json_matches = session.get(query)
    except requests.exceptions.ConnectionError:
        logging.error('Error con la conexión a internet')
        json_matches = None
    except requests.exceptions.Timeout:
        logging.error('Error al intentar acceder a las páginas')
        json_matches = None
    else:
        if json_matches.status_code == 200:
            logger.info('Datos descargados')
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            with open(f'json/{now}.json', 'w', encoding='utf-8') as f:
                try:
                    json.dump(json_matches.json(), f, ensure_ascii=False, indent=4)
                except json.decoder.JSONDecodeError as error:
                    logger.error('Error de json')
            json_matches = json_matches.json()
        else:
            json_matches = None
    return json_matches
def transform_matches(json_matches, last_match):
    logger.info('Transformando datos')
    obtained_matches = len(json_matches)
    valid_matches = 0
    invalid_matches = 0
    old_matches = 0
    list_matches = []
    list_matches_players = []
    matches_processed = 0
    for match in json_matches:
        matches_processed = matches_processed + 1
        # Obtener un json tratable
        actual_string = json.dumps(match)
        valid_match = True

        ranked = match['ranked']
        game_type = match['game_type']
        leaderboard_id = match['leaderboard_id']
        jugadores = match['players']
        if int(match['match_id']) <= last_match:
            old_matches = old_matches + 1
            valid_match = False
        if game_type is None or ranked is None or not ranked or leaderboard_id is None:
            valid_match = False

        for jugador in jugadores:
            civ = jugador['civ']
            won = jugador['won']
            team = jugador['team']
            slot = jugador['slot']
            if slot is None or civ is None or int(civ) == 0 or won is None or team is None:  # check civ and victory
                valid_match = False
        if valid_match:
            # Obtenemos los datos relevantes
            match_id = int(match['match_id'])
            num_players = int(match['num_players'])
            game_type = int(match['game_type'])
            map_size = int(match['map_size'])
            map_type = int(match['map_type'])
            leaderboard_id = int(match['leaderboard_id'])
            rating_type = int(match['rating_type'])
            started = int(match['started'])
            finished = int(match['finished'])
            version = None if match['version'] is None else int(match['version'])
            list_matches.append([match_id, num_players, game_type, map_size, map_type, leaderboard_id, rating_type, started, finished, version])

            players = match['players']
            for player in players:
                profile_id = int(player['profile_id'])
                steam_id = None if player['steam_id'] is None else int(player['steam_id'])
                country = None if player['country'] is None else str(player['country'])[:2]
                slot = int(player['slot'])
                slot_type = int(player['slot_type'])
                rating = None if player['rating'] is None else int(player['rating'])
                rating_change = None if player['rating_change'] is None else int(player['rating_change'])
                color = None if player['color'] is None else int(player['color'])
                team = int(player['team'])
                civ = int(player['civ'])
                won = int(player['won'])
                list_matches_players.append([match_id, slot, profile_id, steam_id, country, slot_type, rating, rating_change, color, team, civ, won])
        else:
            invalid_matches = invalid_matches + 1
        if matches_processed % 100 == 0:
            logger.info(f'Procesados {matches_processed} matches')
    valid_matches = obtained_matches - invalid_matches
    logger.info('Partidas: ' + str(obtained_matches))
    logger.info('Partidas inválidas: ' + str(invalid_matches))
    logger.info('Partidas existentes: ' + str(old_matches))
    logger.info('Partidas válidas: ' + str(valid_matches))
    if valid_matches > 0:
        dataframe_matches = pd.DataFrame(list_matches, columns=['match_id', 'num_players', 'game_type', 'map_size', 'map_type', 'leaderboard_id', 'rating_type', 'started', 'finished', 'version'])
        dataframe_matches_players = pd.DataFrame(list_matches_players, columns=['match_id', 'slot', 'profile_id', 'steam_id', 'country', 'slot_type', 'rating', 'rating_change', 'color', 'team', 'civ', 'won'])
        return [dataframe_matches, dataframe_matches_players]
    else:
        return None
def load_matches(dataframes, last_match):
    logger.info('Cargando a la BD')
    dataframe_matches = dataframes[0]
    dataframes_matches_players = dataframes[1]

    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    engine = db.create_engine(sql_connection)
    try:
        dataframe_matches.to_sql(
            'matches',
            con=engine.connect(),
            if_exists='append',
            index=False,
            dtype={
                'match_id': Integer(),
                'num_players': SmallInteger(),
                'game_type': SmallInteger(),
                'map_size': SmallInteger(),
                'map_type': SmallInteger(),
                'leaderboard_id': SmallInteger(),
                'rating_type': SmallInteger(),
                'started': Integer(),
                'finished': Integer(),
                'version': Integer()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los matches')
    # TODO: find a better way
    with engine.connect() as con:
        if last_match == 0:
            con.execute('ALTER TABLE matches ADD PRIMARY KEY (match_id);')
    try:
        dataframes_matches_players.to_sql(
            'matches_players',
            con=engine.connect(),
            if_exists='append',
            index=False,
            dtype={
                'match_id': Integer(),
                'slot': SmallInteger(),
                'profile_id': Integer(),
                'steam_id': BigInteger(),
                'country': NCHAR(2),
                'slot_type': SmallInteger(),
                'rating': SmallInteger(),
                'rating_change': SmallInteger(),
                'color': SmallInteger(),
                'team': SmallInteger(),
                'civ': SmallInteger(),
                'won': Boolean()
            }
        )
    except exc.SQLAlchemyError:
        logging.error('Error en la conexión a la base de datos')
        raise Exception('Error al conectar a la base de datos')
    else:
        logger.info('Cargados los matches_players')
    # TODO: find a better way
    with engine.connect() as con:
        if last_match == 0:
            con.execute('ALTER TABLE matches_players ADD PRIMARY KEY (match_id, slot);')

def update_db():
    specific_timestamp = datetime(2022, 3, 4, 0, 0)  # Year, month, day, hour, minutes
    one_hour = timedelta(weeks=0, days=0, hours=1, minutes=0)
    for i in range(0, 24 * 16):
        # specific_timestamp = datetime(2022, 3, 4, i, 0)  # Year, month, day, hour, minutes
        iterable_timestamp = specific_timestamp + one_hour * i
        timestamp = trunc(time.mktime(iterable_timestamp.timetuple()))
        etl_matches(timestamp)

def etl_matches(param_timestamp):
    last_match = get_last_match()
    session = requests.Session()
    json_matches = extract_matches(param_timestamp, session)
    if json_matches is None:
        logger.info('No se pudieron cargar partidas de la web')
    else:
        dataframes = transform_matches(json_matches, last_match)
    # logger.info(dataframes)
    if dataframes is not None:
        load_matches(dataframes, last_match)
    else:
        logger.info('No hay partidas nuevas por cargar')

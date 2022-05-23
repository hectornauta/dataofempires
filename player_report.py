# Input with Username
# Search exact match
# Offer steam_id if nothing is found
# ?
# Profit
import json
import logging
import requests
from datetime import datetime

import pandas as pd
import numpy as np

import query_functions

from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

import gamedata

import pickle

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def get_profile_id(steam_id=-1, name=''):
    '''
    Dado un steam_id o username, devuelve el profile_id
    '''
    if steam_id != -1:
        with open('json/players.json') as file_players:
            players = json.load(file_players)
        try:
            player = list(filter(lambda item: item['steam_id'] == steam_id, players))[0]
        except IndexError as e:
            profile_id = -1
        else:
            profile_id = player['profile_id']
            logger.info(profile_id)
    else:
        with open('json/players.json') as file_players:
            players = json.load(file_players)
        try:
            player = list(filter(lambda item: item['name'] == name, players))[0]
        except IndexError as e:
            profile_id = -1
        else:
            profile_id = player['profile_id']
            logger.info(profile_id)
    return profile_id

def get_player_matches(profile_id, number_of_matches=1000):
    logger.info('Generando request')
    query = query_functions.get_generic_player_all_history(profile_id, number_of_matches)
    logger.info(f'Query creada: {query}')
    logger.info('Realizando request')
    session = requests.Session()
    try:
        json_matches = session.get(query)
    except requests.exceptions.ConnectionError:
        logging.error('Error con la conexión a internet')
        raise Exception('Error con la conexión a internet')
        json_matches = None
    except requests.exceptions.Timeout:
        logging.error('Error de Timeout al acceder a las páginas')
        raise Exception('Error de Timeout al acceder a las páginas')
        json_matches = None
    else:
        if json_matches.status_code == 200:
            logger.info('Datos descargados')
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            with open(f'dumps/{now}.json', 'w', encoding='utf-8') as f:
                try:
                    json.dump(json_matches.json(), f, ensure_ascii=False, indent=4)
                except json.decoder.JSONDecodeError as error:
                    logger.error('Error de json')
            json_matches = json_matches.json()
        else:
            json_matches = None
    if json_matches is None:
        return None
    logger.info('Limpiando datos')
    obtained_matches = len(json_matches)
    list_matches_players = []
    matches_processed = 0
    invalid_matches = 0
    valid_matches = 0
    logging.info(type(json_matches))
    for match in json_matches:
        matches_processed = matches_processed + 1
        # Obtener un json tratable
        actual_string = json.dumps(match)
        valid_match = True

        ranked = match['ranked']
        game_type = match['game_type']
        leaderboard_id = match['leaderboard_id']
        jugadores = match['players']
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
                name = None if player['name'] is None else (str(player['name']))[:32]
                team = int(player['team'])
                civ = int(player['civ'])
                won = int(player['won'])
                list_matches_players.append(
                    [
                        match_id,
                        slot,
                        profile_id,
                        steam_id,
                        country,
                        slot_type,
                        rating,
                        rating_change,
                        color,
                        team,
                        civ,
                        won,
                        map_type,
                        leaderboard_id,
                        started,
                        finished
                    ]
                )
        else:
            invalid_matches = invalid_matches + 1
        if matches_processed % 100 == 0:
            logger.info(f'Procesados {matches_processed} matches')
    valid_matches = obtained_matches - invalid_matches
    logger.info('Partidas: ' + str(obtained_matches))
    logger.info('Partidas inválidas: ' + str(invalid_matches))
    logger.info('Partidas válidas: ' + str(valid_matches))
    if valid_matches > 0:
        dataframe_matches_players = pd.DataFrame(
            list_matches_players, columns=[
                'match_id',
                'slot',
                'profile_id',
                'steam_id',
                'country',
                'slot_type',
                'rating',
                'rating_change',
                'color',
                'team',
                'civ',
                'won',
                'map_type',
                'leaderboard_id',
                'started',
                'finished'
            ]
        )
        return dataframe_matches_players
    else:
        return None

def get_player_civ_rates(player_matches, ladder='3', profile_id=220170):
    dataframe_civ = gamedata.civs()
    dataframe_civ = dataframe_civ.reset_index()

    # logger.info(player_matches)
    # logger.info(dataframe_civ)
    # logger.info(player_matches)

    player_matches = player_matches[player_matches['leaderboard_id'] == int(ladder)]
    player_matches = player_matches[player_matches['profile_id'] == int(profile_id)]
    number_of_matches = player_matches['match_id'].nunique()
    player_matches['number_of_wins'] = 0
    player_matches = dataframe_civ.merge(player_matches, left_on='id', right_on='civ', how='outer')
    player_matches = player_matches.groupby(['name', 'nombre']).agg(
        number_of_wins=pd.NamedAgg(column="won", aggfunc="sum"),
        number_of_picks=pd.NamedAgg(column="id", aggfunc="count"))
    player_matches['winrate'] = (player_matches['number_of_wins'] / player_matches['number_of_picks'])
    player_matches['pickrate'] = (player_matches['number_of_picks'] / number_of_matches)
    player_matches = player_matches.sort_values(by='winrate', ascending=False)

    player_matches = player_matches.reset_index()
    player_matches['image'] = player_matches['name'].apply(gamedata.get_civ_asset_name)

    # player_matches = player_matches.drop(['number_of_picks', 'number_of_wins'], axis=1)
    # player_matches['ladder_cat'] = labels
    player_matches = player_matches.rename(
        columns={
            'image': 'Emblema',
            'name': 'Civilization',
            'nombre': 'Civilización',
            'number_of_wins': 'Victorias',
            'number_of_picks': 'Partidas',
            'winrate': 'Porcentaje de victorias',
            'pickrate': 'Porcentaje de uso'
        }
    )
    player_matches = player_matches[[
        'Emblema',
        'Civilización',
        'Civilization',
        'Partidas',
        'Victorias',
        'Porcentaje de victorias',
        'Porcentaje de uso'
    ]]
    logger.info(player_matches)
    return player_matches

def get_enemy_civ_rates(player_matches, ladder='3', profile_id=220170):
    dataframe_civ = gamedata.civs()
    dataframe_civ = dataframe_civ.reset_index()

    player_matches = player_matches[player_matches['leaderboard_id'] == int(ladder)]
    player_matches = player_matches[player_matches['profile_id'] != int(profile_id)]
    number_of_matches = player_matches['match_id'].nunique()
    player_matches['number_of_wins'] = 0
    player_matches = dataframe_civ.merge(player_matches, left_on='id', right_on='civ', how='outer')
    player_matches = player_matches.groupby(['name', 'nombre']).agg(
        number_of_wins=pd.NamedAgg(column="won", aggfunc="sum"),
        number_of_picks=pd.NamedAgg(column="id", aggfunc="count"))
    player_matches['winrate'] = (player_matches['number_of_wins'] / player_matches['number_of_picks'])

    player_matches = player_matches.reset_index()
    player_matches['image'] = player_matches['name'].apply(gamedata.get_civ_asset_name)

    player_matches['pickrate'] = (player_matches['number_of_picks'] / number_of_matches)
    player_matches = player_matches.sort_values(by='winrate', ascending=False)
    player_matches = player_matches.rename(
        columns={
            'image': 'Emblema',
            'name': 'Civilization',
            'nombre': 'Civilización',
            'number_of_wins': 'Derrotas',
            'number_of_picks': 'Partidas',
            'winrate': 'Porcentaje de derrotas',
            'pickrate': 'Porcentaje de aparición'
        }
    )
    player_matches = player_matches[[
        'Emblema',
        'Civilización',
        'Civilization',
        'Partidas',
        'Derrotas',
        'Porcentaje de derrotas',
        'Porcentaje de aparición'
    ]]
    logger.info(player_matches)
    return player_matches

def get_player_map_rates(player_matches, ladder='3', profile_id=220170):
    dataframe_map = gamedata.maps()
    dataframe_map = dataframe_map.reset_index()

    # logger.info(player_matches)
    # logger.info(dataframe_civ)
    # logger.info(player_matches)

    player_matches = player_matches[player_matches['leaderboard_id'] == int(ladder)]
    player_matches = player_matches[player_matches['profile_id'] == int(profile_id)]
    number_of_matches = player_matches['match_id'].nunique()
    player_matches['number_of_wins'] = 0
    player_matches = dataframe_map.merge(player_matches, left_on='id', right_on='map_type', how='outer')
    pd.set_option('display.max_columns', None)
    player_matches = player_matches.groupby(['name', 'nombre']).agg(
        number_of_wins=pd.NamedAgg(column="won", aggfunc="sum"),
        number_of_picks=pd.NamedAgg(column="id", aggfunc="count"))
    player_matches['winrate'] = (player_matches['number_of_wins'] / player_matches['number_of_picks'])
    player_matches['pickrate'] = (player_matches['number_of_picks'] / number_of_matches)
    player_matches = player_matches.sort_values(by='winrate', ascending=False)

    player_matches = player_matches.reset_index()
    player_matches = player_matches[player_matches.number_of_picks > 1]
    # player_matches['image'] = player_matches['name'].apply(gamedata.get_civ_asset_name)

    # player_matches = player_matches.drop(['number_of_picks', 'number_of_wins'], axis=1)
    # player_matches['ladder_cat'] = labels

    logger.info(player_matches)
    player_matches = player_matches.rename(
        columns={
            'name': 'Map',
            'nombre': 'Mapa',
            'number_of_wins': 'Victorias',
            'number_of_picks': 'Partidas',
            'winrate': 'Porcentaje de victorias',
            'pickrate': 'Porcentaje de aparición'
        }
    )
    player_matches = player_matches[[
        'Mapa',
        'Map',
        'Partidas',
        'Victorias',
        'Porcentaje de victorias',
        'Porcentaje de aparición'
    ]]
    logger.info(player_matches)
    return player_matches
def get_player_time_rates(player_matches, ladder='3', profile_id=220170):

    player_matches = player_matches[player_matches['leaderboard_id'] == int(ladder)]
    player_matches = player_matches[player_matches['profile_id'] == int(profile_id)]
    number_of_matches = player_matches['match_id'].nunique()
    player_matches['seconds'] = player_matches['finished'] - player_matches['started']
    player_matches['minutes'] = player_matches['seconds'] / 60
    player_matches = player_matches[['seconds', 'minutes', 'won']]
    # player_matches['ladder_cat'] = labels
    player_matches = player_matches.rename(
        columns={
            'seconds': 'Segundos',
            'minutes': 'Minutos',
            'won': 'Victoria'
        }
    )
    logger.info(player_matches)
    return player_matches

def get_all_stats(player_matches, profile_id=220170):
    dataframe_player = player_matches
    dataframe_player = dataframe_player[dataframe_player['profile_id'] == int(profile_id)]
    dataframe_player = dataframe_player.sort_values(by='finished')
    dataframe_player = dataframe_player.groupby(['leaderboard_id']).agg(
        wins=pd.NamedAgg(column="won", aggfunc="sum"),
        matches=pd.NamedAgg(column="profile_id", aggfunc="count"),
        actual_elo=pd.NamedAgg(column="rating", aggfunc="last"),
        max_elo=pd.NamedAgg(column="rating", aggfunc="max"),
    )
    dataframe_player['losses'] = dataframe_player['matches'] - dataframe_player['wins']
    dataframe_player['winrate'] = dataframe_player['wins'] / dataframe_player['matches']
    dataframe_player['winrate'] = dataframe_player['winrate'] * 100
    dataframe_player['winrate'] = dataframe_player['winrate'].map('{:,.2f} %'.format)
    # Transformación HTML
    dict_leaderboard = {
        0: 'No ranked',
        3: 'Mapa aleatorio solo',
        4: 'Mapa aleatorio por equipos',
        13: 'Guerras Imperiales solo',
        14: 'Guerras Imperiales por equipos'
    }
    dataframe_player = dataframe_player.reset_index()
    dataframe_player = dataframe_player.replace({"leaderboard_id": dict_leaderboard})
    dataframe_player = dataframe_player.rename(
        columns={
            'leaderboard_id': 'Modo',
            'matches': 'Partidas',
            'wins': 'Victorias',
            'losses': 'Derrotas',
            'winrate': 'Winrate',
            'actual_elo': 'Elo actual',
            'max_elo': 'Elo máximo',
        }
    )

    logger.info(dataframe_player)
    return dataframe_player

if __name__ == "__main__":
    TEST = True
    if TEST:
        file_matches = open('files/player_matches.obj', 'rb')
        player_matches = pickle.load(file_matches)
        # get_player_civ_rates(player_matches, ladder='4')
        # get_enemy_civ_rates(player_matches, ladder='3')
        get_player_map_rates(player_matches, ladder='4')
        # get_all_stats(player_matches, 1194828)
        # get_player_time_rates(player_matches, ladder='4')
    else:
        profile_id = get_profile_id(name='DS_Jokerwin')
        player_matches = get_player_matches(profile_id)
        # player_matches = get_dataframe_with_json()
        # get_player_civ_rates(player_matches, ladder='4')
        # get_enemy_civ_rates(player_matches, ladder='4')
        # get_player_map_rates(player_matches, ladder='4')
        get_all_stats(player_matches, 1194828)
        # get_player_time_rates(player_matches, ladder='4')

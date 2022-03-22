import json
import logging
import requests

import psycopg2

from db import conectar
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("log_cargarJSON.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()
# Leaderboard ID (Unranked=0, 1v1 Deathmatch=1, Team Deathmatch=2, 1v1 Random Map=3, Team Random Map=4, 1v1 Empire Wars=13, Team Empire Wars=14)
# 1628294400
# 1628298000
# 1628301600

CIVS = pd.read_csv('civs.csv')
CIVS.drop(['numero'], axis=1, inplace=True)
CIVS.set_index('id', inplace=True)
# logger.info(CIVS)

list_units = []

def create_dataunit(winner_civ, defeated_civ, winner_elo, defeated_elo, map_type):
    list_units.append([winner_civ, defeated_civ, winner_elo, defeated_elo, map_type])

def extract_player_matches(player_id):
    query = get_player_matches(player_id, 1000)
    logger.info(query)

    partidas = requests.get(query)
    partidas = partidas.json()
    obtained_matches = len(partidas)
    valid_matches = 0
    invalid_matches = 0
    old_matches = 0

    dataframe_performance = CIVS.copy()
    dataframe_performance['wins'] = 0
    dataframe_performance['defeats'] = 0
    dataframe_performance['rival_wins'] = 0
    dataframe_performance['rival_defeats'] = 0
    logger.info(f'Initial \n{dataframe_performance}')

    wins = 0
    defeats = 0
    active_leaderboard = 3
    for partida in partidas:
        # Obtener un json tratable
        cadena = json.dumps(partida)
        valid_match = True

        # game_type = partida['game_type']
        # map_type = partida['map_type']
        ranked = partida['ranked']
        leaderboard_id = partida['leaderboard_id']
        jugadores = partida['players']
        if ranked is None or leaderboard_id is None:
            valid_match = False
        for jugador in jugadores:
            civ = jugador['civ']
            won = jugador['won']
            if civ is None or int(civ) == 0 or won is None:  # check civ
                valid_match = False
        if leaderboard_id != active_leaderboard:
            valid_match = False
        if valid_match:
            # obtener su id
            match_identificador = int(partida['match_id'])
            match_id = partida['match_id']
            match_uuid = partida['match_uuid']
            num_players = partida['num_players']
            game_type = partida['game_type']
            map_size = partida['map_size']
            map_type = partida['map_type']
            ranked = partida['ranked']
            leaderboard_id = partida['leaderboard_id']
            rating_type = partida['rating_type']
            victory = partida['victory']
            victory_time = partida['victory_time']
            opened = partida['opened']
            started = partida['started']
            finished = partida['finished']

            param_map_type = map_type

            jugadores = partida['players']
            for jugador in jugadores:
                profile_id = jugador['profile_id']
                steam_id = jugador['steam_id']
                name = jugador['name']
                clan = jugador['clan']
                country = jugador['country']
                slot = jugador['slot']
                slot_type = jugador['slot_type']
                rating = jugador['rating']
                rating_change = jugador['rating_change']
                color = jugador['color']
                team = jugador['team']
                civ = jugador['civ']
                won = jugador['won']
                if str(player_id) == steam_id:
                    if won:
                        param_winner_civ = civ
                        param_winner_elo = rating
                        wins = wins + 1
                        dataframe_performance.at[int(civ), 'wins'] = dataframe_performance.at[int(civ), 'wins'] + 1
                    elif not won:
                        param_defeated_civ = civ
                        param_defeated_elo = rating
                        defeats = defeats + 1
                        dataframe_performance.at[int(civ), 'defeats'] = dataframe_performance.at[int(civ), 'defeats'] + 1
                else:
                    if won:
                        param_winner_civ = civ
                        param_winner_elo = rating
                        dataframe_performance.at[int(civ), 'rival_wins'] = dataframe_performance.at[int(civ), 'rival_wins'] + 1
                    elif not won:
                        param_defeated_civ = civ
                        param_defeated_elo = rating
                        dataframe_performance.at[int(civ), 'rival_defeats'] = dataframe_performance.at[int(civ), 'rival_defeats'] + 1
            create_dataunit(param_winner_civ, param_defeated_civ, param_winner_elo, param_defeated_elo, param_map_type)

        else:
            invalid_matches = invalid_matches + 1
    valid_matches = obtained_matches - invalid_matches

    dataframe_performance['win_percent'] = 100 * dataframe_performance['wins'] / (dataframe_performance['wins'] + dataframe_performance['defeats'])
    dataframe_performance['rival_win_percent'] = 100 * dataframe_performance['rival_wins'] / (dataframe_performance['rival_wins'] + dataframe_performance['rival_defeats'])

    dataframe_units = pd.DataFrame(list_units, columns=['param_winner_civ', 'param_defeated_civ', 'param_winner_elo', 'param_defeated_elo', 'param_map_type'])

    logger.info(dataframe_performance)
    logger.info(dataframe_units)

    logger.info('Partidas: ' + str(obtained_matches))
    logger.info('Partidas válidas: ' + str(valid_matches))
    logger.info('Partidas inválidas: ' + str(invalid_matches))
    logger.info('Partidas ganadas: ' + str(wins))
    logger.info('Partidas perdidas: ' + str(defeats))

def extract_matches(param_timestamp):
    # Conexión con BD
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute('SELECT match_id FROM partidas ORDER BY match_id DESC LIMIT 1')
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error('Error al obtener el último match')
        conexion.rollback()
    else:
        conexion.commit()
    last_match = cursor.fetchall()
    logger.info(last_match)
    last_match = int(last_match[0][0])
    # last_match = 140063221

    number_of_matches = 1000
    timestamp = param_timestamp
    query = get_matches(number_of_matches, timestamp)
    # logger.info(query)
    partidas = requests.get(query)
    partidas = partidas.json()

    obtained_matches = len(partidas)
    valid_matches = 0
    invalid_matches = 0
    old_matches = 0
    for partida in partidas:
        # Obtener un json tratable
        # logger.info(partida)
        cadena = json.dumps(partida)
        # logger.info(cadena)
        valid_match = True

        # game_type = partida['game_type']
        # map_type = partida['map_type']
        ranked = partida['ranked']
        leaderboard_id = partida['leaderboard_id']
        jugadores = partida['players']
        if int(partida['match_id']) <= last_match:
            old_matches = old_matches + 1
            valid_match = False
        if ranked is None or leaderboard_id is None:
            valid_match = False
            # print('Partida no valida')
            # print(str(game_type) + ' ' + str(leaderboard_id))

        for jugador in jugadores:
            civ = jugador['civ']
            won = jugador['won']
            if civ is None or int(civ) == 0 or won is None:  # check civ
                valid_match = False
                # print('jugador con datos no válidos')
                # print(str(civ) + ' ' + str(won))
        if valid_match:
            # obtener su id
            match_identificador = int(partida['match_id'])
            # Insertar en la DB
            try:
                cursor.execute("INSERT INTO matches_info(json,match_id) VALUES (%s,%s)", (cadena, match_identificador))
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                logger.error('Error al insertar en matches')
                conexion.rollback()
                continue
            else:
                conexion.commit()
            match_id = partida['match_id']
            match_uuid = partida['match_uuid']
            num_players = partida['num_players']
            game_type = partida['game_type']
            map_size = partida['map_size']
            map_type = partida['map_type']
            ranked = partida['ranked']
            leaderboard_id = partida['leaderboard_id']
            rating_type = partida['rating_type']
            victory = partida['victory']
            victory_time = partida['victory_time']
            opened = partida['opened']
            started = partida['started']
            finished = partida['finished']
            try:
                cursor.execute("INSERT INTO partidas(match_id,match_uuid,num_players,game_type,map_size,map_type,ranked,leaderboard_id,rating_type,victory,victory_time,opened,started,finished) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                    match_id,
                    match_uuid,
                    num_players,
                    game_type,
                    map_size,
                    map_type,
                    ranked,
                    leaderboard_id,
                    rating_type,
                    victory,
                    victory_time,
                    opened,
                    started,
                    finished))
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                logger.error('Error al insertar en partidas')
                conexion.rollback()
                continue
            else:
                conexion.commit()

            jugadores = partida['players']
            for jugador in jugadores:
                profile_id = jugador['profile_id']
                steam_id = jugador['steam_id']
                name = jugador['name']
                clan = jugador['clan']
                country = jugador['country']
                slot = jugador['slot']
                slot_type = jugador['slot_type']
                rating = jugador['rating']
                rating_change = jugador['rating_change']
                color = jugador['color']
                team = jugador['team']
                civ = jugador['civ']
                won = jugador['won']
                try:
                    cursor.execute("INSERT INTO jugadores_x_partidas(match_id,match_uuid,profile_id,steam_id,name,clan,country,slot,slot_type,rating,rating_change,color,team,civ,won) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                        match_id,
                        match_uuid,
                        profile_id,
                        steam_id,
                        name,
                        clan,
                        country,
                        slot,
                        slot_type,
                        rating,
                        rating_change,
                        color,
                        team,
                        civ,
                        won))
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(error)
                    logger.error('Error al insertar en jugadores_en_partidas')
                    conexion.rollback()
                    break
                else:
                    conexion.commit()
        else:
            invalid_matches = invalid_matches + 1
    valid_matches = obtained_matches - invalid_matches
    logger.info('Partidas: ' + str(obtained_matches))
    logger.info('Partidas inválidas: ' + str(invalid_matches))
    logger.info('Partidas existentes: ' + str(old_matches))
    logger.info('Partidas válidas: ' + str(valid_matches))

    # identificador = partida['match_uuid']
    # cadena =  'https://aoe2.net/api/match?uuid=' + identificador
    # partida_info = http2.request('GET',cadena)
    # partida_info = json.loads(partida_info.data.decode('utf-8'))
    # print(partida_info)
    conexion.close()
    cursor.close()

def get_player_matches(steam_id, number_of_matches):
    query = f'https://aoe2.net/api/player/matches?game=aoe2de&steam_id={steam_id}&count={number_of_matches}'
    return query
def get_player_history(steam_id, number_of_matches, leaderboard_id):
    query = f'https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id={leaderboard_id}&steam_id={steam_id}&count={number_of_matches}'
    return query
def get_matches(number_of_matches, start_time):
    query = f'https://aoe2.net/api/matches?game=aoe2de&count={number_of_matches}&since={start_time}'
    return query
def get_match_details_match_id(match_id):
    query = f'https://aoe2.net/api/match?match_id={match_id}'
    return query
def get_match_details_uuid(uuid):
    query = f'https://aoe2.net/api/match?uuid={uuid}'
    return query

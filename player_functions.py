import json
import requests

import psycopg2

import pandas as pd

import query_functions
import etl
import sql_functions

import logging_config

logger = logging_config.configure_logging('player_functions')

CIVS = pd.read_csv('csv/civs.csv')
CIVS.drop(['numero'], axis=1, inplace=True)
CIVS.set_index('id', inplace=True)

list_units = []

def create_solo_dataunit(winner_civ, defeated_civ, winner_elo, defeated_elo, map_type):
    list_units.append([winner_civ, defeated_civ, winner_elo, defeated_elo, map_type])

def create_tg_dataunit(json_match):
    list_match = []
    partida = json_match
    match_id = int(partida['match_id'])
    num_players = int(partida['num_players'])
    map_type = int(partida['map_type'])
    started = int(partida['started'])
    finished = int(partida['finished'])

    list_match.append(match_id)
    list_match.append(num_players)
    duration = finished - started
    list_match.append(started)
    list_match.append(duration)

    temp_list_players = []
    jugadores = partida['players']
    for jugador in jugadores:
        rating = int(jugador['rating'])
        civ = int(jugador['civ'])
        won = bool(jugador['won'])
        temp_list_players.append(rating)
        temp_list_players.append(civ)
        temp_list_players.append(won)
    for i in range(8 - num_players):
        temp_list_players.append(None)
        temp_list_players.append(None)
        temp_list_players.append(None)
    list_match.append(temp_list_players)  # TODO: convertir a tupla
    logger.info(list_match)

def get_player_matches_by_nickname(username):
    profile_id = get_player_profile_id(username)
    profile_id = str(profile_id[0][0])
    logger.info(profile_id)
    matches = extract_player_matches(profile_id)
    logger.info(matches)

def get_player_profile_id(steam_name):
    return sql_functions.get_profile_ids(steam_name)

def extract_player_matches(player_id):
    query = query_functions.get_generic_player_all_history(player_id, 1000)
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

        # map_type = partida['map_type']
        ranked = partida['ranked']
        game_type = partida['game_type']
        leaderboard_id = partida['leaderboard_id']
        jugadores = partida['players']
        if game_type is None or ranked is None or not ranked or leaderboard_id is None:
            valid_match = False
        for jugador in jugadores:
            civ = jugador['civ']
            won = jugador['won']
            team = jugador['team']
            slot = jugador['slot']
            if slot is None or civ is None or int(civ) == 0 or won is None or team is None:  # check civ and victory
                valid_match = False
        if leaderboard_id != active_leaderboard:
            valid_match = False
        if leaderboard_id == 4:
            create_tg_dataunit(partida)
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
            create_solo_dataunit(param_winner_civ, param_defeated_civ, param_winner_elo, param_defeated_elo, param_map_type)

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
    return dataframe_units

def transform_player_matches(ilst_of_matches):
    dataframe = pd.DataFrame()
    return dataframe

if __name__ == "__main__":
    # REPORTS = []
    # REPORTS.append(countries_elo_stats())
    # show_all_reports()
    get_player_matches_by_nickname('Hectornauta')

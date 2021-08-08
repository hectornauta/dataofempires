import urllib3
import json
import psycopg2

from db import conectar
import pandas as pd

conexion = conectar()
cursor = conexion.cursor()

#print(len(partidas))

for partida in partidas:
    cadena = json.dumps(partida)
    #cursor.execute("INSERT INTO matches(json) VALUES (%s)",(cadena,))
    

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
        cursor.execute("INSERT INTO partidas(match_id,match_uuid,num_players,game_type,map_size,map_type,ranked,leaderboard_id,rating_type,victory,victory_time,opened,started,finished) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(match_id,match_uuid,num_players,game_type,map_size,map_type,ranked,leaderboard_id,rating_type,victory,victory_time,opened,started,finished))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    #identificador = partida['match_uuid']
    #cadena =  'https://aoe2.net/api/match?uuid=' + identificador
    #partida_info = http2.request('GET',cadena)
    #partida_info = json.loads(partida_info.data.decode('utf-8'))
    #print(partida_info)
conexion.commit()
conexion.close()
cursor.close()
print('Hello')
import urllib3
import json
import psycopg2

from db import conectar
import pandas as pd

conexion = conectar()
cursor = conexion.cursor()

http = urllib3.PoolManager()
#http2 = urllib3.PoolManager()

partidas = http.request('GET','https://aoe2.net/api/matches?game=aoe2de&count=1000&since=1628298000')

#1628294400
#1628298000
#1628301600
partidas = json.loads(partidas.data.decode('utf-8'))

#print(len(partidas))
total_partidas = len(partidas)
total_partidas_validas = 0
total_partidas_invalidas = 0
for partida in partidas:
    #Obtener un json tratable
    cadena = json.dumps(partida)
    
    partida_valida = True

    #game_type = partida['game_type']
    #map_type = partida['map_type']
    ranked = partida['ranked']
    leaderboard_id = partida['leaderboard_id']
    jugadores = partida['players']

    if ranked==None or leaderboard_id==None:
        partida_valida=False
        #print('Partida no valida')
        #print(str(game_type) + ' ' + str(leaderboard_id))

    for jugador in jugadores:
        civ = jugador['civ']
        won = jugador['won']
        if civ == None or int(civ)==0 or won==None: #check civ
            partida_valida=False
            #print('jugador con datos no válidos')
            #print(str(civ) + ' ' + str(won))
    
    if partida_valida:
        #obtener su id
        match_identificador = int(partida['match_id'])
        #Insertar en la DB
        try:
            cursor.execute("INSERT INTO matches(json,match_id) VALUES (%s,%s)",(cadena,match_identificador))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print('Error al insertar en matches')
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
            cursor.execute("INSERT INTO partidas(match_id,match_uuid,num_players,game_type,map_size,map_type,ranked,leaderboard_id,rating_type,victory,victory_time,opened,started,finished) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(match_id,match_uuid,num_players,game_type,map_size,map_type,ranked,leaderboard_id,rating_type,victory,victory_time,opened,started,finished))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print('Error al insertar en partidas')
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
                cursor.execute("INSERT INTO jugadores_en_partidas(match_id,match_uuid,profile_id,steam_id,name,clan,country,slot,slot_type,rating,rating_change,color,team,civ,won) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(match_id,match_uuid,profile_id,steam_id,name,clan,country,slot,slot_type,rating,rating_change,color,team,civ,won))
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                print('Error al insertar en jugadores_en_partidas')
                conexion.rollback()
                break
            else:
                conexion.commit()
        else:
            total_partidas_invalidas = total_partidas_invalidas + 1
total_partidas_validas = total_partidas - total_partidas_invalidas
print('Partidas: ' + str(total_partidas))
print('Partidas inválidas: ' + str(total_partidas_invalidas))
print('Partidas válidas: ' + str(total_partidas_validas))



    #identificador = partida['match_uuid']
    #cadena =  'https://aoe2.net/api/match?uuid=' + identificador
    #partida_info = http2.request('GET',cadena)
    #partida_info = json.loads(partida_info.data.decode('utf-8'))
    #print(partida_info)
conexion.close()
cursor.close()
print('Hello')
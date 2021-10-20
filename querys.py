import urllib3
import json
import psycopg2
import csv

from db import conectar
import pandas as pd

conexion = conectar()
cursor = conexion.cursor()

elementos = []
cursor.execute("SELECT J.country,J.rating,C.nombre,J.won FROM jugadores_en_partidas AS J INNER JOIN partidas AS P ON J.match_id=P.match_id INNER JOIN civilizaciones AS C ON C.numero=J.civ WHERE ranked=True AND P.leaderboard_id = 3")
elementos = cursor.fetchall()

tabla = []
cursor.execute("SELECT C.nombre FROM civilizaciones AS C")
tabla = cursor.fetchall()
print(tabla)



with open('Example.csv', 'w', newline = '', encoding="utf-8") as csvfile:
    my_writer = csv.writer(csvfile, delimiter = ';')
    my_writer.writerows(elementos)

conexion.commit()
conexion.close()
cursor.close()
print('Todo finalizóp sin errores')
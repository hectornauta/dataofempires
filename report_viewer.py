import logging
import os

from decouple import config

import pandas as pd
import sqlalchemy as db
from sqlalchemy import exc
import numpy as np
import random
from math import sqrt

import plotly.express as px

from plotly.subplots import make_subplots
import plotly.graph_objects as go

DIR = os.path.dirname(__file__)

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

def show_all_reports():
    REPORTS = []
    REPORTS.append(civ_rates())
    REPORTS.append(civ_win_rates())
    REPORTS.append(civ_pick_rates())
    REPORTS.append(elo_distribution())
    return REPORTS

def elo_distribution():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_1vs1_players_elo.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_players_elo = pd.read_sql_query(sql_query, sql_connection)
    # create the bins
    counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 3000, 50))
    bins = 0.5 * (bins[:-1] + bins[1:])

    figure_elo_distribution = px.bar(x=bins, y=counts, labels={'x': 'elo', 'y': 'Cantidad de players'})
    return figure_elo_distribution

def civ_rates():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_civ_rates = pd.read_sql_query(sql_query, sql_connection)
    dataframe_civ_rates.set_index('id', inplace=True)
    dataframe_civ_rates['rate'] = np.sqrt((dataframe_civ_rates['winrate']) ** 2 + (40 + dataframe_civ_rates['pickrate']) ** 2)

    figure_civ_rates = px.scatter(dataframe_civ_rates, x="pickrate", y="winrate", text="nombre", size_max=60, color='rate')
    figure_civ_rates.update_traces(textposition='top center')
    figure_civ_rates.update_layout(
        height=900,
        width=1280,
        title_text='Pick rate and Win rate de Civilizaciones',
        showlegend=False
    )
    figure_civ_rates.update_coloraxes(showscale=False)
    figure_civ_rates.update_traces(showlegend=False)
    figure_civ_rates.update_layout(yaxis_tickformat='.0%')
    figure_civ_rates.update_layout(xaxis_tickformat='.0%')
    return figure_civ_rates

def civ_win_rates():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_civ_rates = pd.read_sql_query(sql_query, sql_connection)
    dataframe_civ_rates.set_index('id', inplace=True)

    figure_win_rates = px.bar(
        dataframe_civ_rates.sort_values(by='winrate', ascending=False),
        x='nombre',
        y='winrate',
        width=1280,
        hover_data={'nombre': True, 'winrate': ':.2%'}, color='winrate',
        labels={'nombre': 'Civilización', 'winrate': 'Porcentaje de victorias'}, height=400
    )
    figure_win_rates.update_coloraxes(showscale=False)
    figure_win_rates.update_layout(
        yaxis_tickformat='.0%',
        title_text='Porcentaje de victorias de civilizaciones'
    )
    return figure_win_rates

def civ_pick_rates():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_civ_rates = pd.read_sql_query(sql_query, sql_connection)
    dataframe_civ_rates.set_index('id', inplace=True)

    figure_pick_rates = px.bar(
        dataframe_civ_rates.sort_values(by='pickrate', ascending=False),
        x='nombre',
        y='pickrate',
        width=1280,
        hover_data={'nombre': True, 'pickrate': ':.2%'}, color='pickrate',
        labels={'nombre': 'Civilización', 'pickrate': 'Porcentaje de veces escogida'}, height=400
    )
    figure_pick_rates.update_coloraxes(showscale=False)
    figure_pick_rates.update_layout(
        yaxis_tickformat='.0%',
        title_text='Porcentaje de uso de civilizaciones'
    )
    return figure_pick_rates

if __name__ == "__main__":
    REPORTS = []
    REPORTS.append(civ_rates())
    show_all_reports(REPORTS)

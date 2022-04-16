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

import sql_functions

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

CIVS = pd.read_csv('csv/civs.csv')
CIVS.drop(['numero'], axis=1, inplace=True)
CIVS.set_index('id', inplace=True)

def show_all_reports():
    REPORTS = []
    REPORTS.append(civ_rates())
    REPORTS.append(civ_win_rates())
    REPORTS.append(civ_pick_rates())
    REPORTS.append(elo_distribution())
    return REPORTS

def get_player_stats():
    # TODO: ranking of civs
    # TODO: Winrates
    # TODO: Maps
    # TODO: elo progression
    return None

def civ_vs_civ(chosen_civ=-1):
    sql_results = sql_functions.get_civ_vs_civ()
    dataframe_civ_vs_civ = pd.DataFrame.from_records(
        sql_results,
        columns=sql_results.keys()
    )
    if chosen_civ != -1:
        dataframe_civ_vs_civ = dataframe_civ_vs_civ.loc[dataframe_civ_vs_civ['civ_1'].isin([chosen_civ])]
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.merge(CIVS, how='left', left_on='civ_1', right_on='id')
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.merge(CIVS, how='left', left_on='civ_2', right_on='id')
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.sort_values(['nombre_x', 'nombre_y'], ascending=[True, True])
    dataframe_civ_vs_civ.drop(['name_y', 'name_x'], axis=1, inplace=True)
    dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['winrate'] * 100
    dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['winrate'].map('{:,.2f} %'.format)
    # logger.info(dataframe_civ_vs_civ)
    figure_civ_vs_civ = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(
                        ['Civilización 1', 'Civilización 2', 'Partidas ganadas', 'Partidas en total', 'Winrate']
                    ),
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[
                        dataframe_civ_vs_civ.nombre_x,
                        dataframe_civ_vs_civ.nombre_y,
                        dataframe_civ_vs_civ.wins,
                        dataframe_civ_vs_civ.matches,
                        dataframe_civ_vs_civ.winrate,
                    ],
                    fill_color='lavender',
                    align='left'
                )
            )
        ]
    )
    return figure_civ_vs_civ

def elo_distribution(ladder=3):
    FILE = f'{DIR}/sql/get_players_elo.sql'
    dataframe_players_elo = sql_functions.get_sql_results(FILE, ladder)
    # create the bins
    if ladder == 3 or ladder == 13:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2500, 50))
    elif ladder == 4:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 3500, 100))
    elif ladder == 13:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2000, 50))
    elif ladder == 14:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2000, 50))
    bins = 0.5 * (bins[:-1] + bins[1:])

    figure_elo_distribution = px.bar(x=bins, y=counts, labels={'x': 'elo', 'y': 'Cantidad de jugadores'})
    # figure_elo_distribution.show()
    return figure_elo_distribution

def countries_elo_stats(ladder=3):
    # TODO: control de errores
    COUNTRIES = pd.read_csv('csv/countries.csv')
    COUNTRIES.set_index('alpha-2', inplace=True)
    FILE = f'{DIR}/sql/get_players_elo.sql'
    dataframe_countries = sql_functions.get_sql_results(FILE, ladder)
    dataframe_countries = dataframe_countries.reset_index()
    dataframe_countries = dataframe_countries.groupby(['country']).agg(
        mean_elo=pd.NamedAgg(column="elo", aggfunc="mean"),
        max_elo=pd.NamedAgg(column="elo", aggfunc="max"),
        std_elo=pd.NamedAgg(column="elo", aggfunc="std"),
        sem_elo=pd.NamedAgg(column="elo", aggfunc="sem"),
        var_elo=pd.NamedAgg(column="elo", aggfunc="var"),
    )
    dataframe_countries = dataframe_countries.reset_index()
    # logger.info(dataframe_countries)
    dataframe_countries_elo = dataframe_countries.merge(COUNTRIES, how='inner', left_on='country', right_on='alpha-2')
    dataframe_countries_elo['mean_elo'] = round(dataframe_countries_elo['mean_elo'])
    # logger.info(dataframe_countries_elo)
    figure_countries_elo = px.choropleth(
        dataframe_countries_elo,
        locations="alpha-3",
        color="mean_elo",  # lifeExp is a column of gapminder
        hover_name='name',  # column to add to hover information
        color_continuous_scale=px.colors.sequential.amp
    )
    figure_countries_elo.update_layout(
        title_text='elo Promedio por país',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='orthographic'
        )
    )
    return figure_countries_elo

def map_playrate():
    FILE = f'{DIR}/sql/get_maps_playrate.sql'
    dataframe_map_playrate = sql_functions.get_sql_results(FILE)
    dataframe_map_playrate.drop(['id'], axis=1, inplace=True)
    # create the bins
    figure_map_playrate = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(
                        dataframe_map_playrate.columns
                    ),
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[
                        dataframe_map_playrate.name,
                        dataframe_map_playrate.nombre,
                        dataframe_map_playrate.playrate,
                        dataframe_map_playrate.number_of_matches
                    ],
                    fill_color='lavender',
                    align='left'
                )
            )
        ]
    )    # figure_elo_distribution.show()
    return figure_map_playrate

def civ_rates(ladder='3A'):
    logger.info(f'Estoy por mostrar un gráfico, valor de ladder: {ladder}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    dataframe_civ_rates = sql_functions.get_sql_results(FILE, ladder)
    dataframe_civ_rates.set_index('id', inplace=True)
    dataframe_civ_rates['rate'] = np.sqrt((dataframe_civ_rates['winrate']) ** 2 + (40 + dataframe_civ_rates['pickrate']) ** 2)
    logger.info(dataframe_civ_rates)
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

def civ_win_rates(ladder='3A'):
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    dataframe_civ_rates = sql_functions.get_sql_results(FILE, ladder)
    dataframe_civ_rates.set_index('id', inplace=True)

    figure_win_rates = px.bar(
        dataframe_civ_rates.sort_values(by='winrate', ascending=False),
        x='nombre',
        y='winrate',
        width=1280,
        hover_data={'nombre': True, 'winrate': ':.2%'}, color='winrate',
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'nombre': 'Civilización', 'winrate': 'Porcentaje de victorias'}, height=400
    )
    figure_win_rates.update_coloraxes(showscale=False)
    figure_win_rates.update_layout(
        yaxis_tickformat='.0%',
        title_text='Porcentaje de victorias de civilizaciones'
    )
    return figure_win_rates

def civ_pick_rates(ladder='3A'):
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    dataframe_civ_rates = sql_functions.get_sql_results(FILE, ladder)
    dataframe_civ_rates.set_index('id', inplace=True)

    figure_pick_rates = px.bar(
        dataframe_civ_rates.sort_values(by='pickrate', ascending=False),
        x='nombre',
        y='pickrate',
        width=1280,
        hover_data={'nombre': True, 'pickrate': ':.2%'}, color='pickrate',
        color_continuous_scale=px.colors.sequential.YlOrBr,
        labels={'nombre': 'Civilización', 'pickrate': 'Porcentaje de veces escogida'}, height=400
    )
    figure_pick_rates.update_coloraxes(showscale=False)
    figure_pick_rates.update_layout(
        yaxis_tickformat='.0%',
        title_text='Porcentaje de uso de civilizaciones'
    )
    return figure_pick_rates

if __name__ == "__main__":
    # REPORTS = []
    # REPORTS.append(countries_elo_stats())
    # show_all_reports()
    civ_vs_civ()

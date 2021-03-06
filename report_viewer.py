import os

from decouple import config

import pandas as pd
import sqlalchemy as db
from sqlalchemy import exc
import numpy as np
import random
from math import sqrt

import plotly.express as px

from dash import html
import dash_bootstrap_components as dbc

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import sql_functions
import gamedata

import flag

DIR = os.path.dirname(__file__)

import logging_config

logger = logging_config.configure_logging('report_viewer')

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
    # REPORTS.append(elo_distribution())
    return REPORTS

def get_player_stats():
    # TODO: ranking of civs
    # TODO: Winrates
    # TODO: Maps
    # TODO: elo progression
    return None

def get_civ_asset_name(x):
    x = x.lower()
    emblem_path = f'/assets/civ_icons/{x}.png'
    # logger.info(emblem_path)
    return html.Img(src=emblem_path, height='30px')

def get_progress_bar(x):
    return dbc.Progress(label=f'{x:.2f} %', value=int(x))

def get_civ_vs_civ_dataframe(chosen_civ=-1, ladder='3A'):
    dataframe_civ_vs_civ = sql_functions.get_civ_vs_civ()
    dataframe_civ_vs_civ = dataframe_civ_vs_civ[['civ_1', 'civ_2', f'wins_{ladder}', f'matches_{ladder}', f'winrate_{ladder}']]

    dataframe_civ_vs_civ = dataframe_civ_vs_civ.rename(
        columns={
            f'wins_{ladder}': 'wins',
            f'matches_{ladder}': 'matches',
            f'winrate_{ladder}': 'winrate'
        }
    )

    if chosen_civ != -1:
        dataframe_civ_vs_civ = dataframe_civ_vs_civ.loc[dataframe_civ_vs_civ['civ_1'].isin([chosen_civ])]
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.merge(CIVS, how='left', left_on='civ_1', right_on='id')
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.merge(CIVS, how='left', left_on='civ_2', right_on='id')
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.dropna()
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.sort_values(['nombre_x', 'nombre_y'], ascending=[True, True])
    dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['winrate'] * 100
    # dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['winrate'].map('{:,.2f} %'.format)
    dataframe_civ_vs_civ['image_x'] = dataframe_civ_vs_civ['name_x'].apply(get_civ_asset_name)
    dataframe_civ_vs_civ['image_y'] = dataframe_civ_vs_civ['name_y'].apply(get_civ_asset_name)
    dataframe_civ_vs_civ.drop(['name_y', 'name_x'], axis=1, inplace=True)
    # logger.info(dataframe_civ_vs_civ)
    dataframe_civ_vs_civ = dataframe_civ_vs_civ[[
        'image_x',
        'nombre_x',
        'image_y',
        'nombre_y',
        'matches',
        'wins',
        'winrate'
    ]]
    dataframe_civ_vs_civ['winrate'] = dataframe_civ_vs_civ['winrate'].apply(get_progress_bar)
    dataframe_civ_vs_civ = dataframe_civ_vs_civ.rename(
        columns={
            'image_x': 'Emblema',
            'nombre_x': 'Civilizaci??n escogida',
            'image_y': 'Emblema enemigo',
            'nombre_y': 'Civilizaci??n enemiga',
            'matches': 'Partidas jugadas',
            'wins': 'Partidas ganadas',
            'winrate': 'Winrate'
        }
    )
    # logger.info(dataframe_civ_vs_civ)
    return dataframe_civ_vs_civ

def civ_vs_civ(chosen_civ=-1, ladder='3A'):
    dataframe_civ_vs_civ = sql_functions.get_civ_vs_civ()
    dataframe_civ_vs_civ = dataframe_civ_vs_civ[['civ_1', 'civ_2', f'wins_{ladder}', f'matches_{ladder}', f'winrate_{ladder}']]

    dataframe_civ_vs_civ = dataframe_civ_vs_civ.rename(
        columns={
            f'wins_{ladder}': 'wins',
            f'matches_{ladder}': 'matches',
            f'winrate_{ladder}': 'winrate'
        }
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
    layout = go.Layout(autosize=True, margin={'l': 0, 'r': 0, 't': 20, 'b': 0})
    figure_civ_vs_civ = go.Figure(
        layout=layout,
        data=[
            go.Table(
                header=dict(
                    values=list(
                        ['Civilizaci??n 1', 'Civilizaci??n 2', 'Partidas ganadas', 'Partidas en total', 'Winrate']
                    ),
                    # fill_color='paleturquoise',
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
                    # fill_color='lavender',
                    align='left'
                )
            )
        ]
    )
    return figure_civ_vs_civ
'''
def elo_distribution(ladder=3):
    logger.info('Reporte de distribuci??n de elo')
    FILE = f'{DIR}/sql/get_players_elo.sql'
    dataframe_players_elo = sql_functions.get_sql_results(FILE, ladder)
    # create the bins
    if ladder == 3 or ladder == 13:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2500, 50))
        logger.info(counts)
        logger.info(bins)
    elif ladder == 4:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 3500, 100))
    elif ladder == 13:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2000, 50))
    elif ladder == 14:
        counts, bins = np.histogram(dataframe_players_elo.elo, bins=range(0, 2000, 50))
    bins = 0.5 * (bins[:-1] + bins[1:])

    figure_elo_distribution = px.bar(x=bins, y=counts, labels={'x': 'elo', 'y': 'Cantidad de jugadores'}, template='plotly_dark')
    # figure_elo_distribution.show()
    return figure_elo_distribution
'''
def get_flag(x):
    return flag.flag(x)

def get_dataframe_countries(ladder=3):
    logger.info('Creando dataframes de pa??ses')
    COUNTRIES = gamedata.countries()
    ladder = str(ladder)

    dataframe_countries = sql_functions.get_countries_elo()
    # logger.info(dataframe_countries)
    dataframe_countries = dataframe_countries[['country', f'number_of_players_{ladder}', f'mean_elo_{ladder}', f'max_elo_{ladder}']]

    dataframe_countries = dataframe_countries.merge(COUNTRIES, how='left', left_on='country', right_on='alpha-2')
    dataframe_countries = dataframe_countries.sort_values(['country'], ascending=True)
    dataframe_countries['flag'] = dataframe_countries['country'].apply(get_flag)

    dataframe_countries = dataframe_countries[[
        'flag',
        'name',
        f'number_of_players_{ladder}',
        f'mean_elo_{ladder}',
        f'max_elo_{ladder}',
        'alpha-3'
    ]]
    dataframe_countries = dataframe_countries.rename(
        columns={
            'flag': 'Bandera',
            'name': 'Nombre',
            f'number_of_players_{ladder}': 'Cantidad de jugadores',
            f'mean_elo_{ladder}': 'Elo promedio',
            f'max_elo_{ladder}': 'Elo m??ximo',
            # 'std_elo': 'Desviaci??n est??ndar',
            # 'sem_elo': 'Error est??ndar',
            # 'var_elo': 'Varianza'
        }
    )
    # logger.info(dataframe_countries)
    dataframe_countries = dataframe_countries.dropna()
    dataframe_countries = dataframe_countries.sort_values(by='Elo promedio', ascending=False)
    dataframe_countries['Elo promedio'] = dataframe_countries['Elo promedio'].astype(int)
    return dataframe_countries

def countries_elo_stats(ladder=3):
    logger.info('Generando mapa mundial por elo')
    dataframe_countries = get_dataframe_countries(ladder)
    '''
    dataframe_countries = dataframe_countries.reset_index()
    dataframe_countries = dataframe_countries.groupby(['country']).agg(
        mean_elo=pd.NamedAgg(column="elo", aggfunc="mean"),
        max_elo=pd.NamedAgg(column="elo", aggfunc="max"),
        std_elo=pd.NamedAgg(column="elo", aggfunc="std"),
        sem_elo=pd.NamedAgg(column="elo", aggfunc="sem"),
        var_elo=pd.NamedAgg(column="elo", aggfunc="var"),
    )
    dataframe_countries = dataframe_countries.reset_index()
    '''
    figure_countries_elo = px.choropleth(
        dataframe_countries,
        locations="alpha-3",
        color="Elo promedio",  # lifeExp is a column of gapminder
        hover_name='Nombre',  # column to add to hover information
        color_continuous_scale=px.colors.sequential.amp
    )
    figure_countries_elo.update_layout(
        template='plotly_dark',
        title_text='Elo promedio por pa??s',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        )
    )
    return figure_countries_elo

def map_playrate():
    FILE = f'{DIR}/sql/get_maps_playrate.sql'
    dataframe_map_playrate = sql_functions.get_sql_results(FILE)
    dataframe_map_playrate.drop(['id'], axis=1, inplace=True)

    dataframe_map_playrate['playrate'] = dataframe_map_playrate['playrate'] * 100
    # dataframe_map_playrate['playrate'] = dataframe_map_playrate['playrate'].apply(get_progress_bar)
    dataframe_map_playrate['playrate'] = dataframe_map_playrate['playrate'].map('{:,.2f} %'.format)

    # logger.info(dataframe_map_playrate)
    dataframe_map_playrate = dataframe_map_playrate.rename(
        columns={
            'name': 'Map',
            'nombre': 'Mapa',
            'number_of_matches': 'N??mero de partidas analizadas',
            'playrate': 'Porcentaje de uso'
        }
    )
    return dataframe_map_playrate  # figure_map_playrate

def civ_rates(ladder='3A'):
    # logger.info(f'Estoy por mostrar un gr??fico, valor de ladder: {ladder}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    dataframe_civ_rates = sql_functions.get_sql_results(FILE, ladder)
    dataframe_civ_rates.set_index('id', inplace=True)
    dataframe_civ_rates['rate'] = np.sqrt((dataframe_civ_rates['winrate']) ** 2 + (40 + dataframe_civ_rates['pickrate']) ** 2)
    dataframe_civ_rates = dataframe_civ_rates.dropna()
    # logger.info(dataframe_civ_rates)
    figure_civ_rates = px.scatter(dataframe_civ_rates, x="pickrate", y="winrate", text="nombre", size_max=60, color='rate')
    figure_civ_rates.update_traces(textposition='top center')
    # TODO: sacar lo de height y weight
    figure_civ_rates.update_layout(
        template='plotly_dark',
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
    dataframe_civ_rates = dataframe_civ_rates.dropna()

    figure_win_rates = px.bar(
        dataframe_civ_rates.sort_values(by='winrate', ascending=False),
        x='nombre',
        y='winrate',
        hover_data={'nombre': True, 'winrate': ':.2%'}, color='winrate',
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'nombre': 'Civilizaci??n', 'winrate': 'Porcentaje de victorias'}, height=400
    )
    figure_win_rates.update_coloraxes(showscale=False)
    figure_win_rates.update_layout(
        template='plotly_dark',
        yaxis_tickformat='.0%',
        title_text='Porcentaje de victorias de civilizaciones'
    )
    return figure_win_rates

def civ_pick_rates(ladder='3A'):
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    dataframe_civ_rates = sql_functions.get_sql_results(FILE, ladder)
    dataframe_civ_rates.set_index('id', inplace=True)
    dataframe_civ_rates = dataframe_civ_rates.dropna()

    figure_pick_rates = px.bar(
        dataframe_civ_rates.sort_values(by='pickrate', ascending=False),
        x='nombre',
        y='pickrate',
        hover_data={'nombre': True, 'pickrate': ':.2%'}, color='pickrate',
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'nombre': 'Civilizaci??n', 'pickrate': 'Porcentaje de veces escogida'}, height=400
    )
    figure_pick_rates.update_coloraxes(showscale=False)
    figure_pick_rates.update_layout(
        template='plotly_dark',
        yaxis_tickformat='.0%',
        title_text='Porcentaje de uso de civilizaciones'
    )
    return figure_pick_rates

if __name__ == "__main__":
    # REPORTS = []
    # REPORTS.append(countries_elo_stats())
    # show_all_reports()
    # civ_vs_civ(1, '3A')
    # countries_elo_stats()
    # get_civ_vs_civ_dataframe()
    get_dataframe_countries()
    # elo_distribution()

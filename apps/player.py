import logging

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pathlib
from app import app

import report_viewer
import player_report

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()
text_input = html.Div(
    [
        dbc.Input(id="input", placeholder="Ingrese su Steam Id", type="text"),
        html.Br(),
        html.P(id="output"),
    ]
)
switches = html.Div(
    [
        dbc.Label("Seleccione los modos de juego que desea analizar"),
        dbc.Checklist(
            options=[
                {"label": "Partidas sin clasificación", "value": 0, "disabled": True},
                {"label": "Mapa Aleatorio solo", "value": 3, "disabled": True},
                {"label": "Mapa Aleatorio por equipos", "value": 4, "disabled": True},
                {"label": "Guerras Imperiales solo", "value": 13, "disabled": True},
                {"label": "Guerras Imperiales por equipos", "value": 14, "disabled": True},
            ],
            value=[2],
            id="switches-input",
            switch=True,
        ),
    ]
)

inputs = html.Div(
    [
        dbc.Form([switches]),
    ]
)

player_report_container = html.Div([
    html.H1('Obtener estadísssssticas personales', className='text-center border rounded', style={"textAlign": "left"})
])

layout = html.Div([
    html.H1(
        'Obtener estadísticas personales',
        className='text-center border rounded',
        style={"textAlign": "left"}
    ),
    # dcc.Input(id='steam_id', value='76561198147771075', type='text'),
    dbc.Input(
        id='username',
        placeholder='DS_Jokerwin',
        type='text'
    ),
    dbc.Button(
        'Buscar',
        id='submit-button-player-report',
        type='submit',
        className="me-2",
        n_clicks=0
    ),
    html.Div(id='player_report', children='Ingrese su id de Steam')
    # dcc.Graph(id='graph1', figure=report_viewer.map_playrate())
])

@app.callback(
    Output('player_report', 'children'),
    [
        # Input('steam_id', 'value'),
        Input('submit-button-player-report', 'n_clicks')
    ],
    [
        State('username', 'value')
    ]
)
def update_output(n_clicks, username_value):
    if n_clicks is None or n_clicks == 0:
        return 'Sin información'
    elif username_value == '' or username_value is None:
        return 'No ha ingresado un steam_id / username'
    else:
        logger.info(username_value)
        player_profile_id = player_report.get_profile_id(name=username_value)
        if player_profile_id == -1 or player_profile_id is None:
            return 'No se ha encontrado su nombre de usuario en la base de datos'
        player_matches = player_report.get_player_matches(player_profile_id)
        stats = player_report.get_all_stats(player_matches, profile_id=player_profile_id)
        table_stats = dbc.Table.from_dataframe(
            stats,
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )

        stats_player_civ = player_report.get_player_civ_rates(player_matches, '4')
        table_player_civ = dbc.Table.from_dataframe(
            stats_player_civ,
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )

        stats_enemy_civ = player_report.get_enemy_civ_rates(player_matches, '3')
        table_enemy_civ = dbc.Table.from_dataframe(
            stats_enemy_civ,
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )

        stats_maps = player_report.get_player_map_rates(player_matches, '3')
        table_maps = dbc.Table.from_dataframe(
            stats_maps,
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )
        return [table_stats, table_player_civ, table_enemy_civ, table_maps]

'''@app.callback(
    Output(
        "output",
        "children"
    ),
    [
        Input(
            "input",
            "value"
        )
    ]
)
def output_text(value):
    return value'''

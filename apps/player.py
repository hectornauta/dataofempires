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

import logging_config

logger = logging_config.configure_logging('player')

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

radioButtonsLadder = html.Div(
    [
        dbc.RadioItems(
            id="radio-player_report_ladder",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {'label': 'No ranked', 'value': '0'},
                {'label': 'Mapa Aleatorio solo', 'value': '3'},
                {'label': 'Mapa Aleatorio por equipos', 'value': '4'},
                {'label': 'Guerras Imperiales solo', 'value': '13'},
                {'label': 'Guerras Imperiales por equipos', 'value': '14'},
            ],
            value='3',
        ),
    ],
    className="radio-group",
)

title_player_stats = html.H2(
    'Estadísticas de las últimas 1000 partidas',
    className='text-center border rounded',
    style={"textAlign": "left"}
)
title_player_civ = html.H2(
    'Rendimiento por civilización',
    className='text-center border rounded',
    style={"textAlign": "left"}
)
title_player_maps = html.H2(
    'Rendimiento por mapa',
    className='text-center border rounded',
    style={"textAlign": "left"}
)
title_enemy_civ = html.H2(
    'Rendimiento ante civilizaciones enemigas (1vs1)',
    className='text-center border rounded',
    style={"textAlign": "left"}
)

inputs = html.Div(
    [
        dbc.Form([switches]),
    ]
)

player_report_container = html.Div([
    html.H1('Obtener estadísticas personales', className='text-center border rounded', style={"textAlign": "left"})
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
        placeholder='Hectornauta',
        type='text'
    ),
    dbc.Button(
        'Buscar',
        id='submit-button-player-report',
        type='submit',
        className="me-2",
        n_clicks=0
    ),
    html.Hr(),
    dbc.Alert(
        "Se están cargando los resultados, este proceso podria durar unos segundos",
        id="alert-loading-player-report",
        is_open=False,
        duration=18000,
    ),
    html.Div(id='player_report', children='Ingrese su nombre de usuario de Steam')
    # dcc.Graph(id='graph1', figure=report_viewer.map_playrate())
])

@app.callback(
    Output("alert-loading-player-report", "is_open"),
    [Input("submit-button-player-report", "n_clicks")],
    [State("alert-loading-player-report", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open

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
            id='table-player_report_stats',
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )
        stats_player_civ = player_report.get_player_civ_rates(player_matches, '-1', profile_id=player_profile_id)
        table_player_civ = dbc.Table.from_dataframe(
            stats_player_civ,
            id='table-player_report_player_civ',
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )
        stats_enemy_civ = player_report.get_enemy_civ_rates(player_matches, '-1', profile_id=player_profile_id)
        table_enemy_civ = dbc.Table.from_dataframe(
            stats_enemy_civ,
            id='table-player_report_player_map',
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )
        stats_maps = player_report.get_player_map_rates(player_matches, '-1', profile_id=player_profile_id)
        table_maps = dbc.Table.from_dataframe(
            stats_maps,
            id='table-player_report_enemy_civ',
            striped=True,
            responsive=True,
            bordered=True,
            hover=True
        )
        return [
            title_player_stats,
            table_stats,
            # radioButtonsLadder,
            title_player_civ,
            table_player_civ,
            title_player_maps,
            table_maps,
            title_enemy_civ,
            table_enemy_civ
        ]

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

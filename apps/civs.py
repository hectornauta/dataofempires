from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib

from app import app
import report_viewer
import gamedata
import logging_config

logger = logging_config.configure_logging('civs')

# TODO: usar gamedata
CIVS = pd.read_csv('csv/civs.csv')
CIVS.drop(['numero', 'name'], axis=1, inplace=True)
CIVS = CIVS.astype({"id": int}, errors='raise')
CIVS = CIVS.rename(columns={'id': 'value', 'nombre': 'label'})
list_of_civs = CIVS.to_dict('records')
# logger.info(list_of_civs)

radioButtonsCivVsCiv = html.Div(
    [
        dbc.RadioItems(
            id="radio-civ_vs_civ_report_ladder",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {'label': 'Mapa Aleatorio 1000-1300', 'value': '3A'},
                {'label': 'Mapa Aleatorio 1300-1600', 'value': '3B'},
                {'label': 'Mapa Aleatorio +1600', 'value': '3C'},
                {'label': 'Guerras Imperiales 900-1200', 'value': '13A'},
                {'label': 'Guerras Imperiales 1200-2000', 'value': '13B'},
            ],
            value='3A',
        ),
    ],
    className="radio-group",
)
radioButtonsCivRates = html.Div(
    [
        dbc.RadioItems(
            id="radio-civ_rates_report_ladder",
            class_name="btn-group",
            input_class_name="btn-check",
            label_class_name="btn btn-outline-primary",
            label_checked_class_name="active",
            options=[
                {'label': 'Mapa Aleatorio 1000-1300', 'value': '3A'},
                {'label': 'Mapa Aleatorio 1300-1600', 'value': '3B'},
                {'label': 'Mapa Aleatorio +1600', 'value': '3C'},
                {'label': 'Mapa Aleatorio TG 1000-1600', 'value': '4A'},
                {'label': 'Mapa Aleatorio TG 1600-2200', 'value': '4B'},
                {'label': 'Mapa Aleatorio TG +2200', 'value': '4C'},
                {'label': 'Guerras Imperiales 900-1200', 'value': '13A'},
                {'label': 'Guerras Imperiales 1200-2000', 'value': '13B'},
                {'label': 'Guerras Imperiales TG 900-1300', 'value': '14A'},
                {'label': 'Guerras Imperiales TG 1300-2000', 'value': '14B'}
            ],
            value='3A',
        ),
    ],
    className="radio-group",
)
'''
radioButtons = dcc.RadioItems(
    id='radio-civs_report_ladder',
    options=[
        {'label': 'Mapa Aleatorio solo 1000-1300', 'value': '3A'},
        {'label': 'Mapa Aleatorio solo 1300-1600', 'value': '3B'},
        {'label': 'Mapa Aleatorio solo +1600', 'value': '3C'},
        {'label': 'Mapa Aleatorio por equipos 1000-1600', 'value': '4A'},
        {'label': 'Mapa Aleatorio por equipos 1600-2200', 'value': '4B'},
        {'label': 'Mapa Aleatorio por equipos +2200', 'value': '4C'},
        {'label': 'Guerras Imperiales solo 900-1200', 'value': '13A'},
        {'label': 'Guerras Imperiales solo 1200-2000', 'value': '13B'},
        {'label': 'Guerras Imperiales por equipos 900-1300', 'value': '14A'},
        {'label': 'Guerras Imperiales por equipos 1300-2000', 'value': '14B'}
    ],
    value='3A'
)
'''

dropdownCivs = dcc.Dropdown(
    id='dropdown-list_of_civs',
    style={
        'color': '#212121',
        'background-color': '#212121',
    },
    options=list_of_civs,
    searchable=False,
    clearable=False,
    value=3
)

table_civ_vs_civ = dbc.Table.from_dataframe(
    report_viewer.get_civ_vs_civ_dataframe(),
    id='table_civ_vs_civ',
    striped=True,
    bordered=True,
    hover=True
)
layout = html.Div([
    html.H1(
        'Estadísticas sobre civilizaciones',
        className='text-center text-primary mb-4',
        style={"textAlign": "center"}
    ),
    radioButtonsCivVsCiv,
    dropdownCivs,
    html.Div(id="table_civ_vs_civ-container"),
    radioButtonsCivRates,
    dcc.Graph(id='graph_civ_rates', figure=report_viewer.civ_rates()),
    dcc.Graph(id='graph_civ_winrate', figure=report_viewer.civ_pick_rates()),
    dcc.Graph(id='graph_civ_pickrate', figure=report_viewer.civ_win_rates())
])

@app.callback(
    Output('table_civ_vs_civ-container', 'children'),
    [
        Input('dropdown-list_of_civs', 'value'),
        Input('radio-civ_vs_civ_report_ladder', 'value')
    ]
)
def update_table_civ_vs_civ(x1, x2):
    dataframe_civ_vs_civ = report_viewer.get_civ_vs_civ_dataframe(x1, x2)
    return dbc.Table.from_dataframe(
        dataframe_civ_vs_civ,
        striped=True,
        responsive=True,
        bordered=True,
        hover=True
    )

@app.callback(
    Output('graph_civ_rates', 'figure'),
    [
        Input('radio-civ_rates_report_ladder', 'value')
    ]
)
def update_graph_civ_rates(selected_value):
    fig = report_viewer.civ_rates(selected_value)
    # logger.info(selected_value)
    return fig
@app.callback(
    Output('graph_civ_winrate', 'figure'),
    [
        Input('radio-civ_rates_report_ladder', 'value')
    ]
)
def update_graph_civ_winrate(selected_value):
    fig = report_viewer.civ_win_rates(selected_value)
    # logger.info(selected_value)
    return fig
@app.callback(
    Output('graph_civ_pickrate', 'figure'),
    [
        Input('radio-civ_rates_report_ladder', 'value')
    ]
)
def update_graph_civ_pick_rate(selected_value):
    fig = report_viewer.civ_pick_rates(selected_value)
    # logger.info(selected_value)
    return fig

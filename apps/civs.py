import logging

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import report_viewer

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

CIVS = pd.read_csv('csv/civs.csv')
CIVS.drop(['numero', 'name'], axis=1, inplace=True)
CIVS = CIVS.astype({"id": int}, errors='raise')
CIVS = CIVS.rename(columns={'id': 'value', 'nombre': 'label'})
list_of_civs = CIVS.to_dict('records')
# logger.info(list_of_civs)


tab1_content = dbc.Card(
    dcc.Dropdown(
        id='dropdown_civ_rates_3',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=[
            {'label': '1000-1300', 'value': '3A'},
            {'label': '1300-1600', 'value': '3B'},
            {'label': '+1600', 'value': '3C'}
        ],
        value='3A'
    )
)

tab2_content = dbc.Card(
    dcc.Dropdown(
        id='dropdown_civ_rates_4',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=[
            {'label': '1000-1600', 'value': '4A'},
            {'label': '1600-2200', 'value': '4B'},
            {'label': '+2200', 'value': '4C'}
        ],
        value='4A'
    )
)

tab3_content = dbc.Card(
    dcc.Dropdown(
        id='dropdown_civ_rates_13',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=[
            {'label': '900-1200', 'value': '13A'},
            {'label': '1200-2000', 'value': '13B'}
        ],
        value='13A'
    )
)

tab4_content = dbc.Card(
    dcc.Dropdown(
        id='dropdown_civ_rates_14',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=[
            {'label': '900-1300', 'value': '14A'},
            {'label': '1300-2000', 'value': '14B'}
        ],
        value='14A'
    )
)

tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Mapa Aleatorio solo",
                    tab_id="tab_rm_solo"
                ),
                dbc.Tab(
                    label="Mapa Aleatorio por equipos",
                    tab_id="tab_rm_tg"
                ),
                dbc.Tab(
                    label="Guerras Imperiales solo",
                    tab_id="tab_ew_solo"
                ),
                dbc.Tab(
                    label="Guerras Imperiales por equipos",
                    tab_id="tab_ew_tg"
                ),
            ],
            id="tabs",
            active_tab="tab_rm_solo",
        ),
        html.Div(id="content"),
    ]
)

card = dbc.Card(
    dcc.Dropdown(
        id='dropdown-civ_vs_civ',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=list_of_civs,
        value=3
    )
)

layout = html.Div([
    html.H1(
        'Estadísticas sobre civilizaciones',
        className='text-center text-primary mb-4',
        style={"textAlign": "center"}
    ),
    card,
    dcc.Graph(id='table_civ_vs_civ', figure=report_viewer.civ_vs_civ()),

    tabs,
    dcc.Graph(id='graph_civ_rates', figure=report_viewer.civ_rates()),
    dcc.Graph(id='graph_civ_winrate', figure=report_viewer.civ_pick_rates()),
    dcc.Graph(id='graph_civ_pickrate', figure=report_viewer.civ_win_rates())
])

@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tab_rm_solo":
        return tab1_content
    elif at == "tab_rm_tg":
        return tab2_content
    elif at == "tab_ew_solo":
        return tab3_content
    elif at == "tab_ew_tg":
        return tab4_content
    return html.P("This shouldn't ever be displayed...")

def create_table_civ_vs_civ(value=-1):
    return report_viewer.civ_vs_civ(value)

@app.callback(
    Output('table_civ_vs_civ', 'figure'),
    [Input('dropdown-civ_vs_civ', 'value')])
def update_table_civ_vs_civ(selected_value):
    fig = report_viewer.civ_vs_civ(selected_value)
    return fig

def create_graph_civ_rates(value='3A'):
    return report_viewer.civ_rates(value)
def create_graph_civ_winrate(value='3A'):
    return report_viewer.civ_win_rates(value)
def create_graph_civ_pick_rate(value='3A'):
    return report_viewer.civ_pick_rates(value)

@app.callback(
    Output('graph_civ_rates', 'figure'),
    [Input('dropdown_civ_rates_3', 'value')])
def update_graph_civ_rates(selected_value):
    fig = create_graph_civ_rates(selected_value)
    logger.info(selected_value)
    return fig
@app.callback(
    Output('graph_civ_winrate', 'figure'),
    [Input('dropdown_civ_rates_3', 'value')])
def update_graph_civ_winrate(selected_value):
    fig = create_graph_civ_winrate(selected_value)
    logger.info(selected_value)
    return fig
@app.callback(
    Output('graph_civ_pickrate', 'figure'),
    [Input('dropdown_civ_rates_3', 'value')])
def update_graph_civ_pick_rate(selected_value):
    fig = create_graph_civ_pick_rate(selected_value)
    logger.info(selected_value)
    return fig

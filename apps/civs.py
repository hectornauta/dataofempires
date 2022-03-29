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
logger.info(list_of_civs)


tab1_content = dbc.Card(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(
                "1000-1300", id="elo_solo_1-button", n_clicks=0
            ),
            dbc.DropdownMenuItem(
                "1300-1600", id="elo_solo_2-button", n_clicks=0
            ),
            dbc.DropdownMenuItem(
                "+1600", id="elo_solo_3-button", n_clicks=0
            ),
        ],
        label="Elo para Mapa aleatorio solo",
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(
                "1400-1800", id="elo_tg_1-button", n_clicks=0
            ),
            dbc.DropdownMenuItem(
                "1800-2200", id="elo_tg_2-button", n_clicks=0
            ),
            dbc.DropdownMenuItem(
                "+2200", id="elo_tg_3-button", n_clicks=0
            ),
        ],
        label="Elo para mapa aleatorio por equipos",
    ),
    className="mt-3",
)

tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Mapa aleatorio 1vs1",
                    tab_id="tab_rm_solo"
                ),
                dbc.Tab(
                    label="Mapa aleatorio por equipos",
                    tab_id="tab_rm_tg"
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
    dcc.Graph(id='graph2', figure=report_viewer.civ_rates()),
    dcc.Graph(id='graph3', figure=report_viewer.civ_pick_rates()),
    dcc.Graph(id='graph4', figure=report_viewer.civ_win_rates())
])

@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tab_rm_solo":
        return tab1_content
    elif at == "tab_rm_tg":
        return tab2_content
    return html.P("This shouldn't ever be displayed...")

def create_table_civ_vs_civ(value=-1):
    return report_viewer.civ_vs_civ(value)

@app.callback(
    Output('table_civ_vs_civ', 'figure'),
    [Input('dropdown-civ_vs_civ', 'value')])
def update_table_civ_vs_civ(selected_value):
    fig = report_viewer.civ_vs_civ(selected_value)
    return fig

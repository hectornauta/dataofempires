from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import report_viewer

card = dbc.Card(
    dcc.Dropdown(
        id='dropdown',
        style={
            'color': '#212121',
            'background-color': '#212121',
        },
        options=[
            {'label': 'Mapa aleatorio solo', 'value': 3},
            {'label': 'Mapa aleatorio por equipos', 'value': 4},
            {'label': 'Guerras imperiales solo', 'value': 13},
            {'label': 'Guerras imperiales por equipos', 'value': 14}
        ],
        value=3
    )
)

layout = html.Div([
    html.H1(
        'Estadísticas sobre jugadores',
        className='text-center text-primary mb-4',
        style={"textAlign": "left"}
    ),
    card,

    dcc.Graph(id='graph1', figure=report_viewer.countries_elo_stats()),
    dcc.Graph(id='graph2', figure=report_viewer.elo_distribution())
])

def create_map_countries(value=3):
    return report_viewer.countries_elo_stats(value)
def create_elo_distribution(value=3):
    return report_viewer.elo_distribution(value)

@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown', 'value')])
def update_map_countries(selected_value):
    fig = create_map_countries(selected_value)
    return fig
@app.callback(
    Output('graph2', 'figure'),
    [Input('dropdown', 'value')])
def update_elo_distribution(selected_value):
    fig = create_elo_distribution(selected_value)
    return fig

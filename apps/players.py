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
        id='dropdown-players_report_ladder',
        options=[
            {'label': 'Mapa aleatorio solo', 'value': 3},
            {'label': 'Mapa aleatorio por equipos', 'value': 4},
            {'label': 'Guerras imperiales solo', 'value': 13},
            {'label': 'Guerras imperiales por equipos', 'value': 14}
        ],
        value=3,
        style={
            'color': '#34495e',
            'background-color': '#BABABA',
        },
    )
)

tableCountries = dbc.Table.from_dataframe(
    report_viewer.get_dataframe_countries(),
    id='table_countries',
    striped=True,
    bordered=True,
    hover=True
)

layout = html.Div([
    html.H1(
        'Estadísticas sobre jugadores',
        className='text-center text-primary mb-4',
        style={"textAlign": "left"}
    ),
    card,
    html.Div(id="table_countries-container"),
    dcc.Graph(id='graph-countries_elo', figure=report_viewer.countries_elo_stats()),
    # dcc.Graph(id='graph-elo_distribution', figure=report_viewer.elo_distribution())
])

@app.callback(
    Output('table_countries-container', 'children'),
    [
        Input('dropdown-players_report_ladder', 'value')
    ]
)
def update_table_countries(selected_value):
    dataframe_countries = report_viewer.get_dataframe_countries(selected_value)
    return dbc.Table.from_dataframe(
        dataframe_countries,
        striped=True,
        responsive=True,
        bordered=True,
        hover=True
    )
@app.callback(
    Output('graph-countries_elo', 'figure'),
    [
        Input('dropdown-players_report_ladder', 'value')
    ]
)
def update_map_countries(selected_value):
    fig = report_viewer.countries_elo_stats(selected_value)
    return fig
'''
@app.callback(
    Output('graph-elo_distribution', 'figure'),
    [
        Input('dropdown-players_report_ladder', 'value')
    ]
)
def update_elo_distribution(selected_value):
    fig = report_viewer.elo_distribution(selected_value)
    return fig
'''

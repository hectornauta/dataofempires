from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import report_viewer

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
                {"label": "Partidas no ranked", "value": 1},
                {"label": "Ranked Mapa aleatorio 1vs1", "value": 2},
                {"label": "Ranked Mapa aleatorio por equipos", "value": 3},
                {"label": "Guerras imperiales 1vs1", "value": 4, "disabled": True},
                {"label": "Guerras imperiales por equipos", "value": 5, "disabled": True},
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

layout = html.Div([
    html.H1(
        'Obtener estadísticas personales',
        className='text-center border rounded',
        style={"textAlign": "left"}
    ),
    text_input,
    inputs
    # dcc.Graph(id='graph1', figure=report_viewer.map_playrate())
])

@app.callback(
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
    return value

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
                {"label": "Partidas sin clasificación", "value": 0, "disabled": True},
                {"label": "Mapa Aleatorio solo", "value": 3},
                {"label": "Mapa Aleatorio por equipos", "value": 4},
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

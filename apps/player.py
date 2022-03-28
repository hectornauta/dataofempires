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


layout = html.Div([
    html.H1(
        'Obtener estadísticas personales',
        className='text-center text-primary mb-4',
        style={"textAlign": "left"}
    ),
    text_input,
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

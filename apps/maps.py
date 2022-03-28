from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import report_viewer

layout = html.Div([
    html.H1(
        'Estadísticas sobre mapas',
        className='text-center text-primary mb-4',
        style={"textAlign": "left"}
    ),

    dcc.Graph(id='graph1', figure=report_viewer.map_playrate())
])

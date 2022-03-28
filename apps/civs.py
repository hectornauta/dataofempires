from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import report_viewer

dropdown_game_mode = html.Div(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    "Mapa Aleatorio Solo", id="game_mode_1", n_clicks=0
                ),
                dbc.DropdownMenuItem(
                    "Mapa Aleatorio por Equipos", id="game_mode_2", n_clicks=0
                ),
            ],
            label="Modo de juego",
        ),
        html.P(id="item-clicks", className="mt-3"),
    ]
)

dropdown_elo = html.Div(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    "1000-1300", id="elo1-button", n_clicks=0
                ),
                dbc.DropdownMenuItem(
                    "1300-1600", id="elo2-button", n_clicks=0
                ),
                dbc.DropdownMenuItem(
                    "+1600", id="elo3-button", n_clicks=0
                ),
            ],
            label="elo",
        ),
        html.P(id="item-clicks", className="mt-3"),
    ]
)

layout = html.Div([
    html.H1(
        'Estadísticas sobre civilizaciones',
        className='text-center text-primary mb-4',
        style={"textAlign": "center"}
    ),

    html.Div([
        html.Div([
            html.Pre(
                children="Escoja rango de elo",
                style={"fontSize": "100%"}
            ),
            dropdown_elo
        ], className='six columns'),

        html.Div([
            html.Pre(
                children="Escoja modo de juego",
                style={"fontSize": "100%"}
            ),
            dropdown_game_mode
        ], className='six columns'),
    ], className='row'),

    dcc.Graph(id='graph2', figure=report_viewer.civ_rates()),
    dcc.Graph(id='graph1', figure=report_viewer.civ_pick_rates()),
    dcc.Graph(id='graph3', figure=report_viewer.civ_win_rates())
])


# @app.callback(
#     Output(component_id='graph1', component_property='figure'),
#     Output(component_id='graph2', component_property='figure'),
#     Output(component_id='graph3', component_property='figure')  # ,
    # [Input(component_id='pymnt-dropdown', component_property='value'),
    # Input(component_id='country-dropdown', component_property='value')]
# )
# def display_value():  # paymnt_chosen, country_chosen):
    # dfg_fltrd = dfg[(dfg['Order Country'] == country_chosen) &
    #                (dfg["Type"] == pymnt_chosen)]
    # dfg_fltrd = dfg_fltrd.groupby(["Customer State"])[['Sales']].sum()
    # dfg_fltrd.reset_index(inplace=True)
    # fig = px.choropleth(dfg_fltrd, locations="Customer State",
    #                    locationmode="USA-states", color="Sales",
    #                    scope="usa")
    # return fig

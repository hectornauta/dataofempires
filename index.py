from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import about
from apps import civs
from apps import maps
from apps import player
from apps import players

SHEEP_LOGO = '/assets/sheep.webp'
ERROR_404 = '/assets/404.jpg'

nav_items = [
    dbc.NavItem(
        dbc.NavLink(
            'Análisis de jugador',
            href='/apps/player',
            className='border rounded'
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            'Civilizaciones',
            href='/apps/civs',
            className='border rounded'
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            'Mapas',
            href='/apps/maps',
            className='border rounded'
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            'Jugadores', href='/apps/players',
            className='border rounded'
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            'Acerca de',
            href='/apps/about',
            className='border rounded'
        )
    )
]

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=SHEEP_LOGO, height='30px')),
                        dbc.Col(dbc.NavbarBrand('Logo', className='ms-2')),
                    ],
                    align='center',
                    className='g-0',
                ),
                href='',
                style={'textDecoration': 'none'},
            ),
            dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
            dbc.Collapse(
                nav_items,
                id='navbar-collapse',
                is_open=False,
                navbar=True,
            ),
        ],
    ),
    color='dark',
    dark=True,
    className='mb-5',
)

page_content = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[])
])

app.layout = html.Div(
    [navbar, page_content]
)

@app.callback(
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open')
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

error_404 = dbc.Row(
    [
        html.H2(
            'Error 404',
            className='text-center text-primary mb-2',
            style={'textAlign': 'center'}
        ),
        html.H3(
            '¿Una página no encontrada?',
            className='text-left text-primary mb-2',
            style={'textAlign': 'left'}
        ),
        html.H3(
            '¡No, una emboscada de los sarracenos!',
            className='text-left text-primary mb-2',
            style={'textAlign': 'left'}
        ),
        dbc.Col(html.Img(src=ERROR_404)),
    ],
    align='center',
    className='g-0',
)

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/apps/player':
        return player.layout
    if pathname == '/apps/civs':
        return civs.layout
    if pathname == '/apps/maps':
        return maps.layout
    if pathname == '/apps/players':
        return players.layout
    if pathname == '/apps/about':
        return about.layout
    else:
        return error_404
if __name__ == '__main__':
    app.run_server(
        debug=True,
        dev_tools_hot_reload=False
    )

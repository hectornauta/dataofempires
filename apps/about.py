from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output
import pathlib
from app import app

cardGithub = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/github.webp",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    dbc.Button(
                        "Github",
                        href="https://github.com/hectornauta",
                        external_link=True,
                        color="primary",
                        class_name='align-self-center'
                    ),
                ],
            ),
        ),
    ],
    style={
        "width": "9rem",
        "height": "9rem"
    },
)
cardLinkedin = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/linkedin.png",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    dbc.Button(
                        "Linkedin",
                        href="https://linkedin.com/in/hectorpollero",
                        external_link=True,
                        color="primary",
                        class_name='align-self-center'
                    ),
                ],
            ),
        ),
    ],
    style={
        "width": "9rem",
        "height": "9rem"
    },
)
cardAUS = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/UTN.jpg",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Universidad Tecnológica Nacional", className="card-title"),
                    html.P(
                        "Analista Universitario de Sistemas (2018)",
                        className="card-text",
                    ),
                ],
            ),
        ),
    ],
    style={"width": "18rem"},
)

cardING = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/UTN.jpg",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Universidad Tecnológica Nacional", className="card-title"),
                    html.P(
                        "Estudiante avanzado (5° año ya cursado) de Ingeniería en Sistemas de Información",
                        className="card-text",
                    ),
                ],
            ),
        ),
    ],
    style={"width": "18rem"},
)

cardEET = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/EET.png",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Escuela de Educación Técnica 24", className="card-title"),
                    html.P(
                        "Técnico en Informática Profesional y Personal",
                        className="card-text",
                    ),
                ],
            ),
        ),
    ],
    style={
        "width": "18rem",
        "height": "18rem"
    },
)

cardPython = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/python.png",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Python", className="card-title"),
                    html.P("Pandas", className="card-text"),
                    html.P("PyQT", className="card-text"),
                    html.P("Plotly", className="card-text"),
                ],
            ),
        ),
    ],
    style={"width": "18rem"},
)

cardData = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/db.webp",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Datos", className="card-title"),
                    html.P("SQLServer Data Tools", className="card-text"),
                    html.P("PostgreSQL", className="card-text"),
                    html.P("PowerBI", className="card-text"),
                    html.P("Redis", className="card-text"),
                ],
            ),
        ),
    ],
    style={"width": "18rem"},
)


cardCloud = dbc.Card(
    [
        dbc.CardImg(
            src="/assets/cloud.png",
            top=True,
            style={"opacity": 0.2},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4("Cloud", className="card-title"),
                    html.P("IBM Watson", className="card-text"),
                    html.P("Apache Airflow", className="card-text"),
                    html.P("Heroku", className="card-text"),
                    html.P("IoT", className="card-text"),
                ],
            ),
        ),
    ],
    style={"width": "18rem"},
)
card = dbc.Card(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.P("Un simple jugador de Age of Empires a quien le gusta trabajar con datos y verlos ordenados y organizados"),
                ],
                title="Información General",
            ),
            dbc.AccordionItem(
                [
                    cardAUS,
                    cardING,
                    cardEET
                ],
                title="Educación",
            ),
            dbc.AccordionItem(
                [
                    cardPython,
                    cardCloud,
                    cardData,
                ],
                title="Tecnologías",
            ),
            dbc.AccordionItem(
                [
                    cardGithub,
                    cardLinkedin,
                ],
                title="Contacto",
            ),
        ],
    )
)

layout = html.Div(
    [
        html.H1(
            'Acerca de Hectornauta',
            className='text-center border rounded',
            style={"textAlign": "left"}
        ),
        card
    ]
)

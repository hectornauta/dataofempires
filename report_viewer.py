import logging
import os

from decouple import config

import pandas as pd
import sqlalchemy as db
from sqlalchemy import exc
import numpy as np
import random

from bokeh.plotting import figure, output_file, show  # ColumnDataSource
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral6
from bokeh.layouts import column
from bokeh.transform import transform

REPORTS = []
DIR = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')

def show_all_reports():
    return REPORTS

def civ_rates():
    sql_connection = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    FILE = f'{DIR}/sql/get_civ_rates.sql'
    try:
        with open(FILE, 'r') as sql_file:
            sql_query = sql_file.read()
    except IOError as e:
        logger.error(f'Error al leer los archivos SQL: {e}')
        raise Exception('Ha ocurrido un error al leer los archivos SQL')
    # engine = db.create_engine(sql_connection)
    dataframe_civ_rates = pd.read_sql_query(sql_query, sql_connection)
    dataframe_civ_rates.set_index('id', inplace=True)

    source = pd.DataFrame(
        dict(
            x=dataframe_civ_rates['pickrate'],
            y=dataframe_civ_rates['winrate'],
            names=dataframe_civ_rates['nombre']
        )
    )
    mapper_rate = linear_cmap(field_name='y', palette=Spectral6, low=0, high=0.5)
    mapper_win_rate = linear_cmap(field_name='y', palette=Spectral6, low=min(dataframe_civ_rates['winrate']), high=max(dataframe_civ_rates['winrate']))
    mapper_pickrate = linear_cmap(field_name='y', palette=Spectral6, low=min(dataframe_civ_rates['pickrate']), high=max(dataframe_civ_rates['pickrate']))

    fig = figure(title='Civilization rates')
    fig.circle('x', 'y', line_color=mapper_rate, color=mapper_rate, fill_alpha=1, size=12, source=source)
    fig.xaxis.axis_label = 'Pick rate'
    fig.yaxis.axis_label = 'Win rate'
    fig.xaxis.formatter = NumeralTickFormatter(format='0 %')
    fig.yaxis.formatter = NumeralTickFormatter(format='0 %')
    labels = LabelSet(x='x', y='y', text='names', text_font_size='9pt', x_offset=5, y_offset=5, source=ColumnDataSource(source), render_mode='canvas')
    fig.add_layout(labels)
    fig.x_range = Range1d(0, 0.1)
    fig.y_range = Range1d(0, 1)

    x = dataframe_civ_rates['nombre']
    y = dataframe_civ_rates['winrate']
    y2 = dataframe_civ_rates['pickrate']

    fig2 = figure(x_range=x, title="Win rates", toolbar_location=None, width=1280)
    fig2.vbar(x=x, top=y, width=0.9, color='red', fill_alpha=0.75)
    fig2.yaxis.formatter = NumeralTickFormatter(format='0 %')
    fig2.xaxis.major_label_text_font_size = '16pt'
    fig2.xgrid.grid_line_color = None
    fig2.xaxis.major_label_orientation = "vertical"
    fig2.y_range.start = 0
    
    fig3 = figure(x_range=x, title="Pick rates", toolbar_location=None, width=1280)
    fig3.vbar(x=x, top=y2, width=0.9, color='blue', fill_alpha=0.75)
    fig3.yaxis.formatter = NumeralTickFormatter(format='0 %')
    fig3.xaxis.major_label_text_font_size = '16pt'
    fig3.xgrid.grid_line_color = None
    fig3.xaxis.major_label_orientation = "vertical"
    fig3.y_range.start = 0

    show(column(fig, fig2, fig3))
if __name__ == "__main__":
    REPORTS = []
    civ_rates()
    show_all_reports()

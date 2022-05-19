import pandas as pd
def civs():
    CIVS = pd.read_csv('csv/civs.csv')
    CIVS.drop(['numero'], axis=1, inplace=True)
    CIVS.set_index('id', inplace=True)
    return CIVS

def maps():
    MAPS = pd.read_csv('csv/maps.csv', sep=';')
    MAPS.set_index('id', inplace=True)
    return MAPS

def countries():
    COUNTRIES = pd.read_csv('csv/countries.csv')
    COUNTRIES.set_index('alpha-2', inplace=True)
    return COUNTRIES

def leaderboards(ladder):
    dict_leaderboards = {
        '0': 'No ranked',
        '3': 'Mapa aleatorio solo',
        '4': 'Mapa aleatorio por equipos',
        '13': 'Guerras Imperiales solo',
        '14': 'Guerras Imperiales por equipos'
    }
    return dict_leaderboards[ladder]

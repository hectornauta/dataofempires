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

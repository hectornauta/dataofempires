import pandas as pd
import os

DIR = os.path.dirname(__file__)
df = pd.read_json(f'{DIR}/maps.json')
df = df.rename(columns={'string': 'name'})
df['nombre'] = df['name']
print(df)
df.to_csv(f'{DIR}/maps.csv', index=None, sep=';')

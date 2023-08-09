import pandas as pd
import os
import re

# note: append every file that is not an error 
def csvs_to_df(dir):
    files = os.listdir(dir)
    list_dfs = []
    for file in files:
        if 'erro' not in file.lower():
            df = pd.read_csv(f'{dir}/{file}', sep=';')
            list_dfs.append(df)   

    final_df = pd.concat(list_dfs, ignore_index=True)

    return final_df


def transform_df(df):
    trans_df = df.copy()

    # reais to float
    trans_df['valor'] = df['valor'].apply(reais_to_float)

    # add column gear (cambio)
    trans_df['cambio'] = df['modelo'].apply(extrai_cambio)

    # add column engine size (tamanho do motor)
    trans_df['tam_motor'] = df['modelo'].apply(extrai_tam_motor)
        

    return trans_df

def reais_to_float(valor):
    valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
    return float(valor)

def extrai_cambio(modelo):
    # semi auto were included in automatico
    match = re.search(r'Aut\.', modelo)
    if match:
        return 'automatico'
    else:
        return 'manual' 

def extrai_tam_motor(modelo):
    match = re.search(r'\d+\.\d+', modelo)
    if match:
        tam = match.group()
        return float(tam)
    else:
        return None    


dir = 'fipe_data'
df = csvs_to_df(dir)
final_df = transform_df(df)

# include dir
final_df.to_csv('database.csv')

import pandas as pd
import os
import re

# note: append every file that is not an error 
def csvs_to_df(dir):
    files = os.listdir(dir)
    list_dfs = []
    for file in files:
        if file == "ref.json":
            continue
        if 'erro' not in file.lower():
            df = pd.read_csv(f'{dir}/{file}', sep=';')
            list_dfs.append(df)   

    final_df = pd.concat(list_dfs, ignore_index=True)

    return final_df


def transform_df(df):
    trans_df = df.copy()

    # mes_ref to int
    trans_df['mes_ref'] = df['mes_ref'].apply(mes_ref_to_int)

    # reais to float
    trans_df['valor'] = df['valor'].apply(reais_to_float)

    # combustivel add eletrics
    trans_df.loc[trans_df.modelo.str.contains('Elétrico', regex=True, na=False), "combustivel"] = 'e'

    # combustivel to char
    trans_df['combustivel'] = trans_df['combustivel'].apply(combustivel_to_char)


    # codigo_fipe to int
    trans_df['codigo_fipe'] = df['codigo_fipe'].apply(codigo_fipe_to_int)

    # add column gear (cambio)
    trans_df['cambio'] = df['modelo'].apply(extrai_cambio)

    # add column engine size (tamanho do motor)
    trans_df['tam_motor'] = df['modelo'].apply(extrai_tam_motor)
        
 
    return trans_df

def mes_ref_to_int(mes):
    if mes == 'janeiro':
        mes = 1
    elif mes == 'fevereiro':
        mes = 2
    elif mes == 'março':
        mes = 3
    elif mes == 'abril':
        mes = 4
    elif mes == 'maio':
        mes = 5
    elif mes == 'junho':
        mes = 6
    elif mes == 'julho':
        mes = 7
    elif mes == 'agosto':
        mes = 8
    elif mes == 'setembro':
        mes = 9
    elif mes == 'outubro':
        mes = 10
    elif mes == 'novembro':
        mes = 11
    else:
        mes == 12
    return mes

def combustivel_to_char(combustivel):
    if combustivel == 'Gasolina':
        combustivel = 'g'
    elif combustivel == 'Álcool':
        combustivel = 'a'
    elif combustivel == 'Diesel':
        combustivel = 'd'
    return combustivel

def filter_eletrics(df):
    print(df)
    match = re.search('Elétrico', df['modelo'])
    if match:
        df['combustivel'] = 'e'
    return

def codigo_fipe_to_int(cod):
    # 012345-7
    return int(''.join(cod.split('-')))


def reais_to_float(valor):
    valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
    return float(valor)

def extrai_cambio(modelo):
    # semi auto were included in automatico
    match = re.search(r'Aut\.', modelo)
    if match:
        return 'a'
    else:
        return 'm' 

def extrai_tam_motor(modelo):
    match = re.search(r'\d+\.\d+', modelo)
    if match:
        tam = match.group()
        return float(tam)
    else:
        return None    


dir = 'data'
df = csvs_to_df(dir)
final_df = transform_df(df)

# include dir
final_df.to_csv('data/database.csv', sep=';')

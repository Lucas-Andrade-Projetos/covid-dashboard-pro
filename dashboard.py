import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

#05-03-2024
#data on influenza cases obtained in https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024
# Configurar a página
st.set_page_config(layout="wide")

# Definir as colunas desejadas
colunas_desejadas = ['DT_NOTIFIC', 'SG_UF_NOT', 'CS_SEXO', 'NU_IDADE_N',
                     'FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA',
                     'DESC_RESP', 'SATURACAO', 'DIARREIA', 'VOMITO',
                     'FADIGA', 'PERD_OLFT', 'PERD_PALA', 'OUTRO_SIN',
                     'VACINA_COV', 'VACINA', 'EVOLUCAO', 'DT_EVOLUCA', 'DT_ENCERRA']

# Função para carregar dados e selecionar colunas
def carregar_dados(file_path, colunas):
    return pd.read_csv(file_path, sep=';', usecols=colunas)

# Carregar os dados
df = carregar_dados('data.csv', colunas_desejadas)
df2 = carregar_dados('data2.csv', colunas_desejadas)
df3 = carregar_dados('data3.csv', colunas_desejadas)

# Concatenar os DataFrames
df_alterado = pd.concat([df, df2, df3], ignore_index=True)

# Mapeamento dos valores para booleanos
mapeamento_booleano = {1: True, 2: False, 9: False}

# Lista das colunas booleanas
colunas_booleanas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA', 'OUTRO_SIN', 'VACINA_COV', 'VACINA']

# Preencher valores nulos com 0 nas colunas booleanas e aplicar o mapeamento
df_alterado[colunas_booleanas] = df_alterado[colunas_booleanas].fillna(0).replace(mapeamento_booleano).astype(bool)

# Preencher valores nulos em 'EVOLUCAO' com 9 e converter para int
df_alterado['EVOLUCAO'] = pd.to_numeric(df_alterado['EVOLUCAO'], errors='coerce').fillna(9).astype(int)

# Ajustar os tipos das colunas de string
df_alterado['SG_UF_NOT'] = df_alterado['SG_UF_NOT'].astype('string')
df_alterado['CS_SEXO'] = df_alterado['CS_SEXO'].astype('string')

# Ajustar o tipo da coluna de idade
df_alterado['NU_IDADE_N'] = df_alterado['NU_IDADE_N'].fillna(0).astype(int)

# Converter colunas de datas
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'], errors='coerce')
df_alterado['DT_EVOLUCA'] = pd.to_datetime(df_alterado['DT_EVOLUCA'], errors='coerce')
df_alterado['DT_ENCERRA'] = pd.to_datetime(df_alterado['DT_ENCERRA'], errors='coerce')

df_alterado
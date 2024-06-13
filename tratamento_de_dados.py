import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

#recarregando dados
#05-23-2024
#data on influenza cases obtained in https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024
df = pd.read_csv('data.csv', sep=';')
#df2 = pd.read_csv('data2.csv', sep=';')
#df3 = pd.read_csv('data3.csv', sep=';')

# Concatenar os DataFrames
#df = pd.concat([df, df2, df3], ignore_index=True)
#df = pd.concat([df], ignore_index=True)
print(df.info())
df

# Selecionar colunas desejadas
colunas_desejadas = ['DT_NOTIFIC', 'SG_UF_NOT','CS_SEXO' ,'NU_IDADE_N'
                     , 'FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA'
                     ,'DESC_RESP', 'SATURACAO', 'DIARREIA', 'VOMITO'
                     ,'FADIGA','PERD_OLFT','PERD_PALA','OUTRO_SIN'
                     ,'VACINA_COV', 'VACINA', 'EVOLUCAO', 'DT_EVOLUCA', 'DT_ENCERRA']
df_alterado = df[colunas_desejadas]
df_alterado

# Contar valores nulos em cada coluna
valores_nulos_por_coluna = df_alterado.isnull().sum()

# Mapeamento dos valores para booleanos
mapeamento_booleano = {1: 1, 2: 0, 9: 0}

# Lista das colunas booleans
colunas_booleanas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA','OUTRO_SIN','VACINA_COV','VACINA']

# Preencher valores nulos com False nas colunas especificadas 
df_alterado[colunas_booleanas] = df_alterado[colunas_booleanas].fillna(0)

# Aplicar a transformação em cada coluna
for coluna in colunas_booleanas:
    df_alterado[coluna] = df_alterado[coluna].replace(mapeamento_booleano)

# Converter colunas para tipos certos
tipos_string = {'SG_UF_NOT': 'string', 'CS_SEXO': 'string'}
df_alterado = df_alterado.astype(tipos_string)
tipos_int = {'NU_IDADE_N': int}

# Aplicar filtro para idades entre 1 e 95 anos
df_alterado = df_alterado[(df_alterado['NU_IDADE_N'] >= 1) & (df_alterado['NU_IDADE_N'] <= 95)]
df_alterado = df_alterado.astype(tipos_int)
df_alterado[colunas_booleanas] = df_alterado[colunas_booleanas].astype(bool)

#tipos data
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'])
df_alterado['DT_EVOLUCA'] = pd.to_datetime(df_alterado['DT_EVOLUCA'])
df_alterado['DT_ENCERRA'] = pd.to_datetime(df_alterado['DT_ENCERRA'])

#Descobrindo a distribuição dos sintomas
# Lista das colunas sintomas
colunas_sintomas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA','OUTRO_SIN']

dados_sintomas = {'sintomas': colunas_sintomas, 
                  'total_de_casos_true': df_alterado[colunas_sintomas].sum().values,
                  'total_de_casos_false': (~df_alterado[colunas_sintomas]).sum().values,
                  'total_de_casos': df_alterado[colunas_sintomas].sum().values + (~df_alterado[colunas_sintomas]).sum().values}

df_sintomas = pd.DataFrame(dados_sintomas)

df_sintomas['porcentagem_casos'] = (df_sintomas['total_de_casos_true'] / df_sintomas['total_de_casos']) * 100


fig = px.bar(df_sintomas, x='sintomas', y='porcentagem_casos', 
             title='Porcentagem de Casos por Sintoma', 
             labels={'sintomas': 'Sintoma', 'porcentagem_casos': 'Porcentagem de Casos (%)'},
             width=800, height=600, orientation='v', color='sintomas',
             color_discrete_sequence=px.colors.qualitative.Dark24)

for index, row in df_sintomas.iterrows():
    fig.add_annotation(x=index, y=row['porcentagem_casos'],
                       text=f'{row["porcentagem_casos"]:.2f}%', showarrow=False,
                       yshift=10, font=dict(size=10))  
fig.update_layout(xaxis_tickangle=-45)
fig.show()


#Distribuição dos casos por mês e ano
df_alterado['Data'] = df_alterado['DT_NOTIFIC'].dt.to_period('M').astype(str)  # Converter para string
contagem_datas = df_alterado['Data'].value_counts().reset_index()
contagem_datas.columns = ['Data', 'Quantidade']
contagem_datas = contagem_datas.sort_values('Data')

fig = px.line(contagem_datas, x='Data', y='Quantidade', 
              title='Evolução dos Casos ao Longo do Tempo',
              labels={'Data': 'Datas', 'Quantidade': 'Número de Casos'},
              width=800, height=500)

fig.update_traces(line=dict(color='blue', width=2), 
                  mode='lines+markers', 
                  marker=dict(color='blue', size=8))

fig.update_xaxes(title_text='Datas',
                 tickangle=-45, 
                 tickvals=contagem_datas['Data'].unique(),  
                 ticktext=[d.strftime('%b %Y') for d in pd.to_datetime(contagem_datas['Data'].unique())],  # Formatar para mostrar o mês e o ano
                 tickmode='array',
                 ticklabelmode='period')

fig.update_yaxes(title_text='Número de Casos', tickformat='d')

fig.show()


#Contagem de vacinados e não vacinados para o covid
df_vacina_cov = df_alterado['VACINA_COV'].value_counts().reset_index()
df_vacina_cov.columns = ['VACINA_COV', 'Contagem']

cores = px.colors.qualitative.Plotly
fig = px.pie(df_vacina_cov, values='Contagem', names='VACINA_COV',
             title='Distribuição de Vacinados da Vacina do COVID-19',
             color_discrete_sequence=cores)
fig.update_traces(textinfo='percent+label')
fig.update_layout(width=700, height=500)

fig.show()

#Contagem de vacinados e não vacinados para a gripe
df_vacina = df_alterado['VACINA'].value_counts().reset_index()
df_vacina.columns = ['VACINA', 'Contagem']

cores = px.colors.qualitative.Plotly
fig = px.pie(df_vacina, values='Contagem', names='VACINA',
             title='Distribuição de Vacinados da Vacina da Gripe',
             color_discrete_sequence=cores)
fig.update_traces(textinfo='percent+label')
fig.update_layout(width=700, height=500)

fig.show()

#Gráfico da distribuição de sexos
df_filtrado = df_alterado[(df_alterado['CS_SEXO'] != 'I') & (df_alterado['CS_SEXO'] != '1')]

sexo_counts = df_filtrado['CS_SEXO'].value_counts()
fig_sexo = px.pie(names=sexo_counts.index, values=sexo_counts.values, color=sexo_counts.index,
                  color_discrete_sequence=px.colors.qualitative.Set2,
                  title='Distribuição dos Casos por Sexo')
fig_sexo.update_traces(textinfo='percent+label', hole=0.4)
fig_sexo.update_layout(height=500, width=700)

fig_sexo.show()

# Calcular a idade média
idade_media = df_filtrado['NU_IDADE_N'].mean()

print(f"A média de idade dos pacientes é de {idade_media:.0f} anos.")

# Calcular a diferença de tempo (em dias) entre 'DT_ENCERRA' e 'DT_NOTIFIC'
df_alterado['Tempo_Processo'] = (df_alterado['DT_ENCERRA'] - df_alterado['DT_NOTIFIC']).dt.days

# Calcular a média do tempo de processo
media_tempo_processo = df_alterado['Tempo_Processo'].mean()

print(f"A média de tempo do processo é de aproximadamente {media_tempo_processo:.2f} dias.")
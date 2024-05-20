import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

#05-03-2024
#data on influenza cases obtained in https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024
df = pd.read_csv('data.csv', sep=';')
df2 = pd.read_csv('data2.csv', sep=';')
df3 = pd.read_csv('data3.csv', sep=';')

# Concatenar os DataFrames
df = pd.concat([df, df2, df3], ignore_index=True)
print(df.info())

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
df_alterado['EVOLUCAO'] = df_alterado['EVOLUCAO'].fillna(9)

# Aplicar a transformação em cada coluna
for coluna in colunas_booleanas:
    df_alterado[coluna] = df_alterado[coluna].replace(mapeamento_booleano)

# Converter colunas para tipos certos
tipos_string = {'SG_UF_NOT': 'string', 'CS_SEXO': 'string'}
df_alterado = df_alterado.astype(tipos_string)
tipos_int = {'NU_IDADE_N': int}

# Verificar quais valores na coluna 'EVOLUCAO' não podem ser convertidos para inteiros
invalid_values = df_alterado[~df_alterado['EVOLUCAO'].apply(lambda x: str(x).isdigit())]['EVOLUCAO']
print(invalid_values)

# Substituir valores inválidos por NaN
df_alterado['EVOLUCAO'] = pd.to_numeric(df_alterado['EVOLUCAO'], errors='coerce')

# Preencher NaN com um valor padrão, por exemplo, 0
df_alterado['EVOLUCAO'].fillna(9, inplace=True)

# Converter para inteiro
df_alterado['EVOLUCAO'] = df_alterado['EVOLUCAO'].astype(int)
df_alterado = df_alterado.astype(tipos_int)
df_alterado[colunas_booleanas] = df_alterado[colunas_booleanas].astype(bool)

#tipos data
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'])
df_alterado['DT_EVOLUCA'] = pd.to_datetime(df_alterado['DT_EVOLUCA'])
df_alterado['DT_ENCERRA'] = pd.to_datetime(df_alterado['DT_ENCERRA'])

# Lista das colunas sintomas
colunas_sintomas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA','OUTRO_SIN']

# Criar um dicionário para armazenar os dados
dados_sintomas = {'sintomas': colunas_sintomas, 
                  'total_de_casos_true': df_alterado[colunas_sintomas].sum().values,
                  'total_de_casos_false': (~df_alterado[colunas_sintomas]).sum().values,
                  'total_de_casos': df_alterado[colunas_sintomas].sum().values + (~df_alterado[colunas_sintomas]).sum().values}
# Criar o novo DataFrame com os dados dos sintomas
df_sintomas = pd.DataFrame(dados_sintomas)

# Calcular a porcentagem de casos com o sintoma
df_sintomas['porcentagem_casos'] = (df_sintomas['total_de_casos_true'] / df_sintomas['total_de_casos']) * 100

# Criar o gráfico de barras com cores diferentes e valores sobre as barras
fig = px.bar(df_sintomas, x='sintomas', y='porcentagem_casos', 
             title='Porcentagem de Casos por Sintoma', 
             labels={'sintomas': 'Sintoma', 'porcentagem_casos': 'Porcentagem de Casos (%)'},
             width=800, height=600, orientation='v', color='sintomas',
             color_discrete_sequence=px.colors.qualitative.Dark24)

# Adicionar valores sobre as barras
for index, row in df_sintomas.iterrows():
    fig.add_annotation(x=index, y=row['porcentagem_casos'],
                       text=f'{row["porcentagem_casos"]:.2f}%', showarrow=False,
                       yshift=10, font=dict(size=10))  # Ajuste de posição e tamanho da fonte

# Rotacionar os rótulos do eixo x para melhorar a legibilidade
fig.update_layout(xaxis_tickangle=-45)

# Mostrar o gráfico
fig.show()

# Converter a coluna 'DT_NOTIFIC' para o tipo datetime
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'])

# Criar uma nova coluna 'Data' apenas com o mês e o ano
df_alterado['Data'] = df_alterado['DT_NOTIFIC'].dt.to_period('M').astype(str)  # Converter para string

# Contar a quantidade de vezes que cada mês aparece
contagem_datas = df_alterado['Data'].value_counts().reset_index()
contagem_datas.columns = ['Data', 'Quantidade']

# Ordenar o DataFrame pela coluna 'Data' para garantir a ordem correta no gráfico
contagem_datas = contagem_datas.sort_values('Data')

# Criar o gráfico de evolução da doença para todos os meses
fig = px.line(contagem_datas, x='Data', y='Quantidade', 
              title='Evolução da Doença ao Longo do Tempo',
              labels={'Data': 'Mês e Ano', 'Quantidade': 'Número de Casos'},
              width=800, height=500)

# Personalizar o estilo das linhas e pontos
fig.update_traces(line=dict(color='blue', width=2), 
                  mode='lines+markers', 
                  marker=dict(color='blue', size=8))

# Ajustar a formatação dos eixos
fig.update_xaxes(title_text='Mês e Ano',  # Título mais descritivo
                 tickangle=-45, 
                 tickvals=contagem_datas['Data'].unique(),  # Usar os valores únicos de meses
                 ticktext=[d.strftime('%b %Y') for d in pd.to_datetime(contagem_datas['Data'].unique())],  # Formatar para mostrar o mês e o ano
                 tickmode='array',
                 ticklabelmode='period')

fig.update_yaxes(title_text='Número de Casos', tickformat='d')

# Mostrar o gráfico
fig.show()

# Converter a coluna 'DT_NOTIFIC' para o tipo datetime
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'])

# Criar uma nova coluna 'Data' apenas com a data (sem hora)
df_alterado['Data'] = df_alterado['DT_NOTIFIC'].dt.date

# Filtrar apenas as datas do mês de março
# Filtrar apenas as datas do mês de março de 2023
df_marco = df_alterado[(df_alterado['DT_NOTIFIC'].dt.month == 3) & (df_alterado['DT_NOTIFIC'].dt.year == 2023)]


# Contar a quantidade de vezes que cada data aparece
contagem_datas = df_marco['Data'].value_counts().reset_index()
contagem_datas.columns = ['Data', 'Quantidade']

# Ordenar o DataFrame pela coluna 'Data' para garantir a ordem correta no gráfico
contagem_datas = contagem_datas.sort_values('Data')

# Criar o gráfico de evolução da doença para o mês de março
fig = px.line(contagem_datas, x='Data', y='Quantidade', 
              title='Evolução da Doença ao Longo do Tempo - Março',
              labels={'Data': 'Data', 'Quantidade': 'Número de Casos'},
              width=800, height=500)

# Personalizar o estilo das linhas e pontos
fig.update_traces(line=dict(color='blue', width=2), 
                  mode='lines+markers', 
                  marker=dict(color='blue', size=8))

# Ajustar a formatação dos eixos
fig.update_xaxes(title_text='Data (Março)',  # Título mais descritivo
                 tickangle=-45, 
                 tickformat='%d',  # Mostrar apenas o dia
                 dtick='D1',  # Intervalo de um dia
                 ticklabelmode='period')
fig.update_yaxes(title_text='Número de Casos', tickformat='d')

# Mostrar o gráfico
fig.show()

# Converter a coluna 'DT_NOTIFIC' para o tipo datetime
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'])

# Criar uma nova coluna 'Data' apenas com o mês e o ano
df_alterado['Data'] = df_alterado['DT_NOTIFIC'].dt.to_period('M').astype(str)  # Converter para string

# Contar a quantidade de vezes que cada mês aparece
contagem_datas = df_alterado['Data'].value_counts().reset_index()
contagem_datas.columns = ['Data', 'Quantidade']

# Ordenar o DataFrame pela coluna 'Data' para garantir a ordem correta no gráfico
contagem_datas = contagem_datas.sort_values('Data')

# Criar o gráfico de evolução da doença para todos os meses
fig = px.line(contagem_datas, x='Data', y='Quantidade', 
              title='Evolução da Doença ao Longo do Tempo',
              labels={'Data': 'Mês e Ano', 'Quantidade': 'Número de Casos'},
              width=800, height=500)

# Personalizar o estilo das linhas e pontos
fig.update_traces(line=dict(color='blue', width=2), 
                  mode='lines+markers', 
                  marker=dict(color='blue', size=8))

# Ajustar a formatação dos eixos
fig.update_xaxes(title_text='Mês e Ano',  # Título mais descritivo
                 tickangle=-45, 
                 tickvals=contagem_datas['Data'].unique(),  # Usar os valores únicos de meses
                 ticktext=[d.strftime('%b %Y') for d in pd.to_datetime(contagem_datas['Data'].unique())],  # Formatar para mostrar o mês e o ano
                 tickmode='array',
                 ticklabelmode='period')

fig.update_yaxes(title_text='Número de Casos', tickformat='d')

# Seu código para selecionar a coluna 'VACINA' e contar os valores
df_vacina_cov = df_alterado['VACINA_COV'].value_counts().reset_index()
df_vacina_cov.columns = ['VACINA_COV', 'Contagem']

# Definir cores personalizadas para cada tipo de vacina
cores = px.colors.qualitative.Plotly

# Criar o gráfico de pizza com Plotly Express e adicionar elementos de design
fig = px.pie(df_vacina_cov, values='Contagem', names='VACINA_COV',
             title='Distribuição de Vacinados da Vacina do COVID-19',
             color_discrete_sequence=cores)

# Adicionar rótulos e percentagens nas fatias do gráfico
fig.update_traces(textinfo='percent+label')

# Ajustar tamanho e layout do gráfico
fig.update_layout(width=700, height=500)

# Mostrar o gráfico
st.plotly_chart(fig)
fig.show()

# Seu código para selecionar a coluna 'VACINA' e contar os valores
df_vacina = df_alterado['VACINA'].value_counts().reset_index()
df_vacina.columns = ['VACINA', 'Contagem']

# Definir cores personalizadas para cada tipo de vacina
cores = px.colors.qualitative.Plotly

# Criar o gráfico de pizza com Plotly Express e adicionar elementos de design
fig = px.pie(df_vacina, values='Contagem', names='VACINA',
             title='Distribuição de Vacinados da Vacina da gripe',
             color_discrete_sequence=cores)

# Adicionar rótulos e percentagens nas fatias do gráfico
fig.update_traces(textinfo='percent+label')

# Ajustar tamanho e layout do gráfico
fig.update_layout(width=700, height=500)

# Mostrar o gráfico
st.plotly_chart(fig)
fig.show()

# Filtrar para excluir o grupo 'I' da coluna 'CS_SEXO'
df_filtrado = df_alterado[(df_alterado['CS_SEXO'] != 'I') & (df_alterado['CS_SEXO'] != '1')]

# Calcular a idade média
idade_media = df_filtrado['NU_IDADE_N'].mean()
print(f"A média de idade dos pacientes é de {idade_media:.0f} anos.")

# Criar um gráfico de pizza com a distribuição dos valores em 'CS_SEXO' e definir uma paleta de cores
sexo_counts = df_filtrado['CS_SEXO'].value_counts()
fig_sexo = px.pie(names=sexo_counts.index, values=sexo_counts.values, color=sexo_counts.index,
                  color_discrete_sequence=px.colors.qualitative.Set2,
                  title='Distribuição dos casos por sexo')

# Personalizar o layout do gráfico
fig_sexo.update_traces(textinfo='percent+label', hole=0.4)

# Definir as dimensões do gráfico
fig_sexo.update_layout(height=500, width=700)
fig_sexo.show()

# Calcular a diferença de tempo (em dias) entre 'DT_EVOLUCA' e 'DT_NOTIFIC'
df_alterado['Tempo_Processo'] = (df_alterado['DT_ENCERRA'] - df_alterado['DT_NOTIFIC']).dt.days

# Excluir valores nulos em 'DT_EVOLUCA'
df_sem_nulos = df_alterado.dropna(subset=['DT_ENCERRA'])

# Calcular a média do tempo de processo
media_tempo_processo = df_sem_nulos['Tempo_Processo'].mean()

print(f"A média de tempo do processo é de aproximadamente {media_tempo_processo:.2f} dias.")
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
#df2 = carregar_dados('data2.csv', colunas_desejadas)
#df3 = carregar_dados('data3.csv', colunas_desejadas)

# Concatenar os DataFrames
#df_alterado = pd.concat([df, df2, df3], ignore_index=True)
df_alterado = pd.concat([df], ignore_index=True)
# Mapeamento dos valores para booleanos
mapeamento_booleano = {1: True, 2: False, 9: False}

# Lista das colunas booleanas
colunas_booleanas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA', 'OUTRO_SIN', 'VACINA_COV', 'VACINA']

# Preencher valores nulos com 0 nas colunas booleanas e aplicar o mapeamento
df_alterado[colunas_booleanas] = df_alterado[colunas_booleanas].fillna(0).replace(mapeamento_booleano).astype(bool)

# Lista das colunas booleanas
colunas_vacinas = ['VACINA_COV', 'VACINA']                 

# Converter valores booleanos para "Vacinado" e "Não Vacinado"
df_alterado[colunas_vacinas] = df_alterado[colunas_vacinas].replace({True: 'Vacinado', False: 'Não Vacinado'})

# Preencher valores nulos em 'EVOLUCAO' com 9 e converter para int
df_alterado['EVOLUCAO'] = pd.to_numeric(df_alterado['EVOLUCAO'], errors='coerce').fillna(9).astype(int)

# Ajustar os tipos das colunas de string
df_alterado['SG_UF_NOT'] = df_alterado['SG_UF_NOT'].astype('string')
df_alterado['CS_SEXO'] = df_alterado['CS_SEXO'].astype('string')

# Ajustar o tipo da coluna de idade
df_alterado['NU_IDADE_N'] = df_alterado['NU_IDADE_N'].fillna(0).astype(int)

# Aplicar filtro para idades entre 1 e 95 anos
df_alterado = df_alterado[(df_alterado['NU_IDADE_N'] >= 1) & (df_alterado['NU_IDADE_N'] <= 95)]

# Converter colunas de datas
df_alterado['DT_NOTIFIC'] = pd.to_datetime(df_alterado['DT_NOTIFIC'], errors='coerce')
df_alterado['DT_EVOLUCA'] = pd.to_datetime(df_alterado['DT_EVOLUCA'], errors='coerce')
df_alterado['DT_ENCERRA'] = pd.to_datetime(df_alterado['DT_ENCERRA'], errors='coerce')

# Ordenar o DataFrame pela coluna 'DT_NOTIFIC'
df_alterado = df_alterado.sort_values(by='DT_NOTIFIC')
df_alterado["Year"] = df_alterado['DT_NOTIFIC'].apply(lambda x: str(x.year))

# Adicionar a opção 'Todos' para os anos
anos_unicos = df_alterado["Year"].unique().tolist()
anos_unicos.insert(0, 'Todos')
year = st.sidebar.selectbox("Ano", anos_unicos)

# Ordenar o DataFrame pela coluna 'SG_UF_NOT'
df_alterado["Estado"] = df_alterado['SG_UF_NOT']

# Adicionar a opção 'Todos' para os estados
estados_unicos = df_alterado["Estado"].unique().tolist()
estados_unicos.insert(0, 'Todos')
estado = st.sidebar.selectbox("Estado", estados_unicos)

# Filtrar o DataFrame com base nas seleções
if year != 'Todos':
    df_alterado = df_alterado[df_alterado["Year"] == year]
if estado != 'Todos':
    df_alterado = df_alterado[df_alterado["Estado"] == estado]

df_filtrado = df_alterado

col1, spacer1, col2, spacer2, col3 = st.columns([1, 0.25, 1, 0.25, 1])
col4, spacer1, col5 = st.columns([1, 0.3, 1])

# Filtrar para excluir o grupo 'I' da coluna 'CS_SEXO'
df_filtrado = df_filtrado[(df_filtrado['CS_SEXO'] != '1')]
# Criar um gráfico de pizza com a distribuição dos valores em 'CS_SEXO' e definir uma paleta de cores
sexo_counts = df_filtrado['CS_SEXO'].value_counts()
fig_sexo = px.pie(names=sexo_counts.index, values=sexo_counts.values, color=sexo_counts.index,
                  color_discrete_sequence=px.colors.qualitative.Set2,
                  title='Distribuição dos casos por sexo')

# Personalizar o layout do gráfico
fig_sexo.update_traces(textinfo='percent+label')

# Definir as dimensões do gráfico
fig_sexo.update_layout(height=350, width=300)

col1.plotly_chart(fig_sexo)

# Seu código para selecionar a coluna 'VACINA' e contar os valores
df_vacina_cov = df_filtrado['VACINA_COV'].value_counts().reset_index()
df_vacina_cov.columns = ['VACINA_COV', 'Contagem']

# Criar o gráfico de pizza com Plotly Express e adicionar elementos de design
fig_cov = px.pie(df_vacina_cov, values='Contagem', names='VACINA_COV',
             title='Vacinados da Vacina do COVID-19',
             color_discrete_sequence=px.colors.qualitative.Set2)

# Adicionar rótulos e percentagens nas fatias do gráfico
fig_cov.update_traces(textinfo='percent+label')

# Ajustar tamanho e layout do gráfico
fig_cov.update_layout(height=350, width=300)

# Mostrar o gráfico
col2.plotly_chart(fig_cov)

# Seu código para selecionar a coluna 'VACINA' e contar os valores
df_vacina = df_filtrado['VACINA'].value_counts().reset_index()
df_vacina.columns = ['VACINA', 'Contagem']

# Criar o gráfico de pizza com Plotly Express e adicionar elementos de design
fig_vac = px.pie(df_vacina, values='Contagem', names='VACINA',
             title='Vacinados da Vacina da gripe',
            color_discrete_sequence=px.colors.qualitative.Set2)

# Adicionar rótulos e percentagens nas fatias do gráfico
fig_vac.update_traces(textinfo='percent+label')

# Ajustar tamanho e layout do gráfico
fig_vac.update_layout(height=350, width=300)

# Mostrar o gráfico
col3.plotly_chart(fig_vac)

# Criar uma nova coluna 'Data' apenas com o mês e o ano
df_filtrado['Data'] = df_filtrado['DT_NOTIFIC'].dt.to_period('M').astype(str)  # Converter para string

# Contar a quantidade de vezes que cada mês aparece
contagem_datas = df_filtrado['Data'].value_counts().reset_index()
contagem_datas.columns = ['Data', 'Quantidade']

# Ordenar o DataFrame pela coluna 'Data' para garantir a ordem correta no gráfico
contagem_datas = contagem_datas.sort_values('Data')

# Criar o gráfico de evolução da doença para todos os meses
fig_mes = px.line(contagem_datas, x='Data', y='Quantidade', 
              title='Evolução da Doença ao Longo do Tempo',
              labels={'Data': 'Mês e Ano', 'Quantidade': 'Número de Casos'},
              width=600, height=400)

# Personalizar o estilo das linhas e pontos
fig_mes.update_traces(line=dict(color='blue', width=2), 
                  mode='lines+markers', 
                  marker=dict(color='blue', size=8))

# Ajustar a formatação dos eixos
fig_mes.update_xaxes(title_text='Mês e Ano',  # Título mais descritivo
                 tickangle=-45, 
                 tickvals=contagem_datas['Data'].unique(),  # Usar os valores únicos de meses
                 ticktext=[d.strftime('%b %Y') for d in pd.to_datetime(contagem_datas['Data'].unique())],  # Formatar para mostrar o mês e o ano
                 tickmode='array',
                 ticklabelmode='period')

fig_mes.update_yaxes(title_text='Número de Casos', tickformat='d')

# Mostrar o gráfico
col4.plotly_chart(fig_mes)

# Lista das colunas sintomas
colunas_sintomas = ['FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
                     'SATURACAO', 'DIARREIA', 'VOMITO', 'FADIGA', 'PERD_OLFT', 
                     'PERD_PALA','OUTRO_SIN']

# Criar um dicionário para armazenar os dados
dados_sintomas = {'sintomas': colunas_sintomas, 
                  'total_de_casos_true': df_filtrado[colunas_sintomas].sum().values,
                  'total_de_casos_false': (~df_filtrado[colunas_sintomas]).sum().values,
                  'total_de_casos': df_filtrado[colunas_sintomas].sum().values + (~df_filtrado[colunas_sintomas]).sum().values}
# Criar o novo DataFrame com os dados dos sintomas
df_sintomas = pd.DataFrame(dados_sintomas)

# Calcular a porcentagem de casos com o sintoma
df_sintomas['porcentagem_casos'] = (df_sintomas['total_de_casos_true'] / df_sintomas['total_de_casos']) * 100

# Criar o gráfico de barras com cores diferentes e valores sobre as barras
fig_sin = px.bar(df_sintomas, x='sintomas', y='porcentagem_casos', 
             title='Porcentagem de Casos por Sintoma', 
             labels={'sintomas': 'Sintomas', 'porcentagem_casos': 'Porcentagem de Casos (%)'},
             width=560, height=400, orientation='v', color='sintomas',
             color_discrete_sequence=px.colors.qualitative.Set2)

# Adicionar valores sobre as barras
for index, row in df_sintomas.iterrows():
    fig_sin .add_annotation(x=index, y=row['porcentagem_casos'],
                       text=f'{row["porcentagem_casos"]:.2f}%', showarrow=False,
                       yshift=10, font=dict(size=10))  # Ajuste de posição e tamanho da fonte

# Rotacionar os rótulos do eixo x para melhorar a legibilidade
fig_sin.update_layout(xaxis_tickangle=-45, bargap=0.2)
# Mostrar o gráfico
col5.plotly_chart(fig_sin)
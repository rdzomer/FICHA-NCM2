# modulos/grafico_base.py (COMPLETO E CORRIGIDO)
import plotly.express as px
import pandas as pd
from babel.numbers import format_decimal

def _gerar_grafico_base(df, tipo_dado, ncm_formatado, last_updated_month, last_updated_year):
    """
    Gera um gráfico de barras base para importações ou exportações (VERSÃO FINAL)
    """
    if df.empty:
        return px.bar()

    df_plot = df.copy()

    # 1. Remover sufixo de mês para 2024
    df_plot['year'] = df_plot['year'].str.replace(r' \(Até mês \d{2}\)', '', regex=True)
    
    # 2. Filtrar dados válidos
    anos_validos = [str(ano) for ano in range(2010, 2026)]
    df_plot = df_plot[df_plot['year'].isin(anos_validos)]

    # 3. Preparar dados numéricos
    coluna_kg = f'{tipo_dado} (KG)'
    df_plot[coluna_kg] = pd.to_numeric(df_plot[coluna_kg], errors='coerce').fillna(0)

    # 4. Definir cores (2025 em destaque)
    df_plot['Cor'] = df_plot['year'].apply(
        lambda x: 'midnightblue' if x == '2025' else 'steelblue'
    )

    # 5. Criar gráfico
    fig = px.bar(df_plot, x='year', y=coluna_kg,
                 color='Cor',
                 color_discrete_map={
                     'steelblue': 'steelblue',
                     'midnightblue': 'midnightblue'
                 },
                 title=f'{tipo_dado} (kg) da NCM {ncm_formatado}, 2010-2025',
                 labels={'year': 'Ano', coluna_kg: f'{tipo_dado} (KG)'})

    # 6. Ajustes finais
    fig.update_layout(
        bargap=0.15,
        xaxis_title='Ano',
        yaxis_title=f'{tipo_dado} em Kilogramas (KG)',
        showlegend=False
    )

    fig.update_xaxes(
        tickmode='array',
        tickvals=df_plot['year'],
        tickangle=45,
        type='category'
    )

    return fig

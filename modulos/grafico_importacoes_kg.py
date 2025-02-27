# grafico_importacoes_kg.py
import plotly.express as px
import pandas as pd
from babel.numbers import format_decimal
from .grafico_base import _gerar_grafico_base

def gerar_grafico_importacoes(df, df_2024_parcial, ncm_formatado, last_updated_month, last_updated_year):
    """
    Gera o gráfico de importações, usando a função base.
    """
    fig = _gerar_grafico_base(df, df_2024_parcial, 'Importações', ncm_formatado, last_updated_month, last_updated_year)

    # (Restante da formatação do eixo Y - não muda)
    max_y = df['Importações (KG)'].max()
    if max_y <= 50000000:
        tick_spacing = 10000000
    elif max_y <= 100000000:
        tick_spacing = 20000000
    else:
        tick_spacing = 50000000

    tickvals = list(range(0, int(max_y) + tick_spacing, tick_spacing))
    ticktext = [format_decimal(val, locale='pt_BR') for val in tickvals]

    fig.update_yaxes(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        dtick=tick_spacing
    )
    return fig

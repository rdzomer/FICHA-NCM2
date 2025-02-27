# grafico_exportacoes_kg.py (refatorado)

import plotly.express as px
import pandas as pd
from babel.numbers import format_decimal
from .grafico_base import _gerar_grafico_base # Importa a função base


def gerar_grafico_exportacoes(df, ncm_formatado, last_updated_month, last_updated_year):
    """
    Gera o gráfico de exportações, usando a função base e formatando o eixo Y.
    """
    fig = _gerar_grafico_base(df, 'Exportações', ncm_formatado, last_updated_month, last_updated_year)

    # Formatação do Eixo Y (específica para exportações)
    max_y = df['Exportações (KG)'].max()
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

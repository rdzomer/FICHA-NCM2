# modulos/grafico_preco_medio_fob.py (COM ESCALA DINÂMICA)
import plotly.graph_objects as go
import pandas as pd
from babel.numbers import format_decimal
from .grafico_base import _calcular_ticks_eixo_y  # Importe a função

def gerar_grafico_preco_medio(df_2025, df_2024_parcial, ncm_formatado):
    """Gera um gráfico de linha com o preço médio (FOB) de importação/exportação."""
    if df_2025 is None or df_2025.empty:
        return go.Figure()

    df_plot = df_2025.copy()
    df_plot['Preco Medio Export (FOB)'] = df_plot['Exportações (FOB)'] / df_plot['Exportações (KG)']
    df_plot['Preco Medio Import (FOB)'] = df_plot['Importações (FOB)'] / df_plot['Importações (KG)']

    if df_2024_parcial is not None and not df_2024_parcial.empty:
        df_2024_parcial = df_2024_parcial.copy()
        last_updated_month = pd.to_datetime(df_2024_parcial['year'].iloc[0], format='%Y (Até mês %m)').month
        df_2024_parcial['year'] = f'2024 (Até mês {str(last_updated_month).zfill(2)})'
        df_2024_parcial['Preco Medio Export (FOB)'] = df_2024_parcial['Exportações (FOB)'] / df_2024_parcial['Exportações (KG)']
        df_2024_parcial['Preco Medio Import (FOB)'] = df_2024_parcial['Importações (FOB)'] / df_2024_parcial['Importações (KG)']
        df_plot = pd.concat([df_plot, df_2024_parcial])

    df_plot['year'] = df_plot['year'].astype(str).str.replace(r' \(Até mês \d{2}\)', '', regex=True)
    anos_validos = [str(ano) for ano in range(2010, 2026)] + [f'2024 (Até mês {str(last_updated_month).zfill(2)})']
    df_plot = df_plot[df_plot['year'].isin(anos_validos)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['year'], y=df_plot['Preco Medio Export (FOB)'], mode='lines+markers', name='Preço Médio Exportação (FOB)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_plot['year'], y=df_plot['Preco Medio Import (FOB)'], mode='lines+markers', name='Preço Médio Importação (FOB)', line=dict(color='red')))

    fig.update_layout(
        title=f'Preço Médio (US$ FOB/KG) de Importação e Exportação - NCM {ncm_formatado}',
        xaxis_title='Ano',
        yaxis_title='Preço Médio (US$ FOB/KG)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis={'type': 'category'}
    )

    # --- Escala Dinâmica do Eixo Y ---
    max_y = max(df_plot['Preco Medio Export (FOB)'].max(), df_plot['Preco Medio Import (FOB)'].max())
    tickvals, ticktext, dtick = _calcular_ticks_eixo_y(max_y)  # Usa a função genérica
    fig.update_yaxes(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        dtick=dtick
    )

    return fig


# modulos/grafico_preco_medio_fob.py (VERSÃO DE ONTEM)
import plotly.graph_objects as go
import pandas as pd
from babel.numbers import format_decimal
from .grafico_base import _calcular_ticks_eixo_y

def gerar_grafico_preco_medio(df_2025, df_2024_parcial, ncm_formatado):
    if df_2025 is None or df_2025.empty:
        return go.Figure()

    # --- Preparar DataFrame de 2025 ---
    df_2025 = df_2025.copy()
    df_2025['Preco Medio Export (FOB)'] = df_2025['Exportações (FOB)'] / df_2025['Exportações (KG)']
    df_2025['Preco Medio Import (FOB)'] = df_2025['Importações (FOB)'] / df_2025['Importações (KG)']
    meses_2025 = df_2025['year'].str.extract(r'\(Até mês (\d+)\)').dropna()[0].astype(int).tolist()
    if not meses_2025:
        meses_2025 = list(range(1, 13))

    # --- Preparar DataFrame de 2024 Parcial ---
    if df_2024_parcial is not None and not df_2024_parcial.empty:
        df_2024_parcial = df_2024_parcial.copy()
        df_2024_parcial['Preco Medio Export (FOB)'] = df_2024_parcial['Exportações (FOB)'] / df_2024_parcial['Exportações (KG)']
        df_2024_parcial['Preco Medio Import (FOB)'] = df_2024_parcial['Importações (FOB)'] / df_2024_parcial['Importações (KG)']
        df_2024_parcial['mes'] = df_2024_parcial['year'].str.extract(r'\(Até mês (\d+)\)').dropna()[0].astype(int)
        df_2024_parcial = df_2024_parcial[df_2024_parcial['mes'].isin(meses_2025)]
        df_2024_parcial['year'] = '2024 (Parcial)'
    else:
        df_2024_parcial = pd.DataFrame(columns=df_2025.columns)

    # --- Combinar os DataFrames ---
    df_2025['mes'] = df_2025['year'].str.extract(r'\(Até mês (\d+)\)').fillna('12').astype(int)
    df_2025['year'] = df_2025['year'].str.replace(r' \(Até mês \d+\)', '', regex=True)
    df_plot = pd.concat([df_2025, df_2024_parcial], ignore_index=True)

    # --- Preparar dados para o gráfico (ORDENAÇÃO CORRETA) ---

    # Ordenação: Tratar '2024 (Parcial)' como se fosse 2026
    def custom_sort_key(row):
        year = row['year']
        month = row['mes']
        if year == '2024 (Parcial)':
            return (2026, month)  # Ordena como 2026
        else:
            return (int(year), month)

    df_plot['sort_key'] = df_plot.apply(custom_sort_key, axis=1)
    df_plot = df_plot.sort_values(by='sort_key').drop(columns=['sort_key'])

    # Criar rótulos do eixo X *após* a ordenação
    df_plot['eixo_x'] = df_plot.apply(lambda row: f"{row['year']}" if row['year'] == '2024 (Parcial)' else f"{row['mes']:02d}/{row['year']}", axis=1)

    # --- Criar o Gráfico ---
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_plot['eixo_x'], y=df_plot['Preco Medio Export (FOB)'],
                             mode='lines+markers', name='Preço Médio Exportação (FOB)',
                             line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=df_plot['eixo_x'], y=df_plot['Preco Medio Import (FOB)'],
                             mode='lines+markers', name='Preço Médio Importação (FOB)',
                             line=dict(color='red')))

    fig.update_layout(
        title=f'Preço Médio (US$ FOB/KG) de Importação e Exportação - NCM {ncm_formatado}',
        xaxis_title='Mês/Ano',
        yaxis_title='Preço Médio (US$ FOB/KG)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # --- Escala Dinâmica do Eixo Y ---
    max_y = max(df_plot['Preco Medio Export (FOB)'].max(), df_plot['Preco Medio Import (FOB)'].max())
    tickvals, ticktext, dtick = _calcular_ticks_eixo_y(max_y)
    fig.update_yaxes(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        dtick=dtick
    )

    return fig

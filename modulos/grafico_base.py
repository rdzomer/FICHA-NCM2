# modulos/grafico_base.py (COMPLETO - COM 2024 PARCIAL NO GRÁFICO)
import plotly.express as px
import pandas as pd
from babel.numbers import format_decimal

def _gerar_grafico_base(df, df_2024_parcial, tipo_dado, ncm_formatado, last_updated_month, last_updated_year):
    """
    Gera um gráfico de barras com dados de 2010-2025 E dados parciais de 2024.
    """
    if df.empty:
        return px.bar()

    df_plot = df.copy()

    # --- Preparação dos dados ---

    # 1. Remover sufixo de mês (se houver)
    df_plot['year'] = df_plot['year'].astype(str).str.replace(r' \(Até mês \d{2}\)', '', regex=True)

    # 2. Filtrar anos válidos (2010-2025)
    anos_validos = [str(ano) for ano in range(2010, 2026)]
    df_plot = df_plot[df_plot['year'].isin(anos_validos)]

    # 3. Preparar dados numéricos
    coluna_kg = f'{tipo_dado} (KG)'
    df_plot[coluna_kg] = pd.to_numeric(df_plot[coluna_kg], errors='coerce').fillna(0)

    # --- Adicionar dados de 2024 Parcial ---

    if df_2024_parcial is not None and not df_2024_parcial.empty:
        df_2024_parcial = df_2024_parcial.copy()
        # Renomear e preparar 2024 parcial
        df_2024_parcial['year'] = f'2024 (Até mês {str(last_updated_month).zfill(2)})'
        df_2024_parcial[coluna_kg] = pd.to_numeric(df_2024_parcial[coluna_kg], errors='coerce').fillna(0)
        # Adicionar ao DataFrame principal
        df_plot = pd.concat([df_plot, df_2024_parcial])


    # --- Configuração do gráfico ---

    # 4. Definir cores
    df_plot['Cor'] = df_plot['year'].apply(
        lambda x: 'midnightblue' if x.startswith('2025') else
        ('darkorange' if x.startswith('2024 (Até') else 'steelblue')
    )

    # 5. Criar gráfico de barras
    fig = px.bar(df_plot, x='year', y=coluna_kg,
                 color='Cor',
                 color_discrete_map={
                     'steelblue': 'steelblue',
                     'midnightblue': 'midnightblue',
                     'darkorange': 'darkorange'
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
        tickvals=df_plot['year'].unique(),  # Usar valores únicos para evitar duplicatas
        tickangle=45,
        type='category'
    )

    return fig

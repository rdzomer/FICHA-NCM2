import plotly.express as px
import pandas as pd
from babel.numbers import format_decimal

def gerar_grafico_importacoes(df, ncm_formatado, last_updated_month, last_updated_year):
    """
    Gera um gráfico de barras das importações em KG para uma dada NCM, de 2010 a 2025,
    incluindo barras para 2024 (completo) e 2024 (parcial) correspondente a 2025 (parcial).

    Args:
        df (pd.DataFrame): DataFrame com os dados ('year', 'month', 'Importações (KG)').
        ncm_formatado (str): Código NCM formatado (ex: "8544.42.00").
        last_updated_month (str): Mês da última atualização (ex: "02").
        last_updated_year (str): Ano da última atualização (ex: "2025").

    Returns:
        plotly.graph_objects.Figure: Objeto Figure do Plotly.
    """
    try:
        df_plot = df.copy()

        # 1. Dados Numéricos e Ano/Mês
        df_plot['Importações (KG)'] = pd.to_numeric(df_plot['Importações (KG)'], errors='coerce').fillna(0)
        df_plot['Ano'] = df_plot['year'].str.extract(r'(\d{4})').astype(int)
        df_plot['month'] = df_plot['year'].str.extract(r'\((\d+)-').fillna(last_updated_month).astype(int)

        # 2. Filtro Temporal (2010-2025)
        df_plot = df_plot[(df_plot['Ano'] >= 2010) & (df_plot['Ano'] <= 2025)]

        # 3. Separação dos Dados (2010-2023, 2024 Completo, 2025 Parcial, 2024 Parcial)
        df_resto = df_plot[(df_plot['Ano'] >= 2010) & (df_plot['Ano'] <= 2023)].copy()
        df_2024_completo = df_plot[df_plot['Ano'] == 2024].copy()  # 2024 COMPLETO
        df_2025_parcial = df_plot[df_plot['Ano'] == 2025].copy()
        df_2024_parcial = df_2024_completo[df_2024_completo['month'] <= int(last_updated_month)].copy()  # 2024 Parcial

        # 4. Preparação para Concatenação (Adiciona 'Tipo' - ORDEM CORRETA AGORA)
        df_resto['Tipo'] = df_resto['Ano'].astype(str)
        df_2024_completo['Tipo'] = '2024'  # 2024 COMPLETO - Mantém como '2024'
        df_2025_parcial['Tipo'] = '2025 (Parcial)'
        df_2024_parcial['Tipo'] = '2024 (Parcial)'


        # 5. Concatenação (ORDEM CORRETA AGORA)
        df_final = pd.concat([df_resto, df_2024_completo, df_2024_parcial, df_2025_parcial])


        # 6. Cores (Mapeamento para 'Tipo')
        colors = {
            '2025 (Parcial)': 'darksalmon',
            '2024 (Parcial)': 'sandybrown',
            '2024': 'orange',  # Cor para 2024 COMPLETO
            **{str(ano): 'orange' for ano in range(2010, 2024)}
        }

        # 7. Criação do Gráfico
        fig = px.bar(df_final, x='Tipo', y='Importações (KG)',
                     color='Tipo',
                     color_discrete_map=colors,
                     title=f'Importações (kg) da NCM {ncm_formatado}, de 2010 a 2025',
                     labels={'Tipo': 'Ano', 'Importações (KG)': 'Importações (KG)'})

        # 8. Formatação do Eixo Y (Corrigido - Pontos em vez de vírgulas)
        max_y = df_final['Importações (KG)'].max()
        if max_y <= 50000000:
            tick_spacing = 10000000
        elif max_y <= 100000000:
            tick_spacing = 20000000
        else:
            tick_spacing = 50000000

        tickvals = list(range(0, int(max_y) + tick_spacing, tick_spacing))
        ticktext = [format_decimal(val, locale='pt_BR') for val in tickvals]  # Formata com pontos

        fig.update_yaxes(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            dtick=tick_spacing  # redundante, mas não prejudicial
        )

        # 9. Rótulos do Eixo X (Ajustado para 'Tipo')
        fig.update_xaxes(
            tickmode='array',
            tickvals=df_final['Tipo'].tolist(),
            ticktext=df_final['Tipo'].tolist(),
            tickangle=45
        )

        # 10. Ajustes de Layout
        fig.update_layout(
            bargap=0.1,
            bargroupgap=0.05,
            showlegend=False  # Remove a legenda
        )

        return fig

    except Exception as e:
        print(f"Erro ao gerar gráfico de importações: {e}")
        return None

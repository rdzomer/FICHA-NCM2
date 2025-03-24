import plotly.graph_objects as go
import pandas as pd

def _calcular_ticks_eixo_y(max_value):
    """Calcula intervalos seguros para diferentes faixas de valores"""
    if max_value == 0:
        return [0, 0.5], ['0.00', '0.50']
    
    step = max_value / 5
    ticks = [i * step for i in range(6)]
    return ticks, [f"{tick:.4f}" for tick in ticks]

def gerar_grafico_preco_medio(df_2025, df_2024_parcial, ncm_formatado, last_updated_month):
    """
    Gera o gráfico de Preço Médio (US$ FOB/KG), exibindo de 2004 até 2025 (parcial),
    e por último o dado de 2024 (parcial).
    """
    import numpy as np  # Caso precise de NumPy em algum ponto

    if df_2025 is None or df_2025.empty:
        return go.Figure()

    try:
        # Copia do DataFrame para não alterar o original
        df_2025 = df_2025.copy()

        # Cálculo do preço médio para 2025
        df_2025['Preco Export'] = df_2025['Exportações (FOB)'] / df_2025['Exportações (KG)']
        df_2025['Preco Import'] = df_2025['Importações (FOB)'] / df_2025['Importações (KG)']
        
        # Cálculo do preço médio para 2024 (parcial)
        df_2024_proc = pd.DataFrame()
        if df_2024_parcial is not None and not df_2024_parcial.empty:
            df_2024_proc = df_2024_parcial.copy()
            df_2024_proc['Preco Export'] = df_2024_proc['Exportações (FOB)'] / df_2024_proc['Exportações (KG)']
            df_2024_proc['Preco Import'] = df_2024_proc['Importações (FOB)'] / df_2024_proc['Importações (KG)']
            df_2024_proc['year'] = f'2024 (Até mês {str(last_updated_month).zfill(2)})'

        # Combinação dos dados
        df_plot = pd.concat([
            df_2025[['year', 'Preco Export', 'Preco Import']],
            df_2024_proc[['year', 'Preco Export', 'Preco Import']]
        ], ignore_index=True)

        # Lógica de ordenação: 2024 parcial vem depois de 2025 parcial
        df_plot['ano_num'] = df_plot['year'].apply(
            lambda x: 2026 if '2024 (Até' in str(x)
                     else (2025 if '2025' in str(x)
                     else int(str(x)[:4]))
        )
        df_plot = df_plot.sort_values('ano_num')

        # Criação do gráfico
        fig = go.Figure()
        
        # Adição das séries
        for serie, cor, nome in [('Preco Export', 'blue', 'Exportação'), 
                                 ('Preco Import', 'red', 'Importação')]:
            fig.add_trace(go.Scatter(
                x=df_plot['year'],
                y=df_plot[serie],
                name=nome,
                mode='lines+markers',
                line=dict(color=cor)
            ))

        # Configuração de layout
        fig.update_layout(
            title=f'Preço Médio - NCM {ncm_formatado}',
            xaxis_title='Ano',
            yaxis_title='US$ FOB/KG',
            xaxis=dict(type='category', tickangle=-45),
            legend=dict(orientation="h", y=1.1),
            height=500
        )

        return fig

    except Exception as e:
        print(f"Erro na geração do gráfico: {str(e)}")
        return go.Figure()


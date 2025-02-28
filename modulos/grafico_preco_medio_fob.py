# modulos/grafico_preco_medio_fob.py
import plotly.graph_objects as go
import pandas as pd

def _calcular_ticks_eixo_y(max_value):
    """Calcula intervalos seguros para diferentes faixas de valores"""
    if max_value == 0:
        return [0, 0.5], ['0.00', '0.50']
    
    step = max_value / 5
    ticks = [i * step for i in range(6)]
    return ticks, [f"{tick:.4f}" for tick in ticks]

def gerar_grafico_preco_medio(df_2025, df_2024_parcial, ncm_formatado):
    if df_2025 is None or df_2025.empty:
        return go.Figure()

    try:
        # Processamento básico dos dados (mantido original)
        df_2025 = df_2025.copy()
        df_2025['Preco Export'] = df_2025['Exportações (FOB)'] / df_2025['Exportações (KG)']
        df_2025['Preco Import'] = df_2025['Importações (FOB)'] / df_2025['Importações (KG)']
        
        # Processamento 2024 (versão simplificada)
        df_2024_proc = pd.DataFrame()
        if df_2024_parcial is not None and not df_2024_parcial.empty:
            df_2024_proc = df_2024_parcial.copy()
            df_2024_proc['Preco Export'] = df_2024_parcial['Exportações (FOB)'] / df_2024_parcial['Exportações (KG)']
            df_2024_proc['Preco Import'] = df_2024_parcial['Importações (FOB)'] / df_2024_parcial['Importações (KG)']
            df_2024_proc['year'] = '2024 (Parcial)'

        # Combinação segura dos dados
        df_plot = pd.concat([
            df_2025[['year', 'Preco Export', 'Preco Import']],
            df_2024_proc[['year', 'Preco Export', 'Preco Import']]
        ], ignore_index=True)

        # Ordenação simplificada
        df_plot['ano_num'] = df_plot['year'].apply(lambda x: 2026 if '2024' in str(x) else int(str(x)[:4]))
        df_plot = df_plot.sort_values('ano_num')

        # Criação do gráfico
        fig = go.Figure()
        
        # Adição das séries (configuração básica)
        for serie, cor, nome in [('Preco Export', 'blue', 'Exportação'), 
                               ('Preco Import', 'red', 'Importação')]:
            fig.add_trace(go.Scatter(
                x=df_plot['year'],
                y=df_plot[serie],
                name=nome,
                mode='lines+markers',
                line=dict(color=cor)
            ))

        # Configuração de layout segura
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

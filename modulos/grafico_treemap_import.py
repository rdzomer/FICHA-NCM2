import plotly.express as px
import pandas as pd

def gerar_treemap_importacoes_2024(df_import_2024_country, ncm_code, ncm_str):
    """
    Gera o Treemap de Importações 2024 (US$ FOB), retornando um objeto Figure.
    
    Parâmetros:
      - df_import_2024_country: DataFrame com as colunas ['country', 'metricFOB'].
      - ncm_code: Código NCM (string).
      - ncm_str: String formatada do NCM para exibição no título.
    
    Retorna:
      - fig_import: Objeto Figure do Plotly contendo o Treemap.
    """
    # Agregar por país para somar o valor total de metricFOB
    df_agg = df_import_2024_country.groupby('country', as_index=False)['metricFOB'].sum()
    
    # Converter metricFOB para numérico (caso esteja como string)
    df_agg['metricFOB'] = pd.to_numeric(df_agg['metricFOB'], errors='coerce').fillna(0)
    
    # Calcular a representatividade
    total_import_fob = df_agg['metricFOB'].sum()
    df_agg['Representatividade (%)'] = (df_agg['metricFOB'] / total_import_fob) * 100

    # Gerar o treemap
    fig_import = px.treemap(
        df_agg, 
        path=['country'], 
        values='metricFOB',
        custom_data=['Representatividade (%)'],
        title=f'Origem das Importações 2024 (US$ FOB) - {ncm_str}'
    )
    
    # Ajustar dimensões e margens
    fig_import.update_layout(
        margin=dict(t=40, l=10, r=10, b=40),
        width=700,   # Largura do gráfico
        height=600,  # Altura do gráfico
    )
    
    fig_import.update_traces(
        textinfo='label+value',
        texttemplate='%{label}<br>US$ %{value:,.2f} (%{customdata[0]:.2f}%)',
        textfont_size=18
    )
    
    return fig_import




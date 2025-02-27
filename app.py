# app.py (COMPLETO - Com Gráficos KG, FOB e Preço Médio)
import streamlit as st
import pandas as pd
from modulos.api_comex import obter_data_ultima_atualizacao, obter_descricao_ncm, obter_dados_comerciais, obter_dados_comerciais_ano_anterior, obter_dados_comerciais_ano_atual
import modulos.processamento as proc
import modulos.grafico_importacoes_kg as graf_kg
import modulos.grafico_exportacoes_kg as graf_exp
import modulos.grafico_importacoes_fob as graf_fob
import modulos.grafico_exportacoes_fob as graf_exp_fob
import modulos.grafico_preco_medio_fob as graf_preco_medio  # Importe o novo módulo
from io import BytesIO
from babel.numbers import format_decimal

def obter_e_processar_dados(ncm_code, tipo, last_updated_month=None, last_updated_year=None):
    """Obtém e processa dados, lidando com diferentes tipos de consulta."""
    if tipo == "2025":
        dados_export, erro_export = obter_dados_comerciais(ncm_code, "export")
        if erro_export: return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais(ncm_code, "import")
        if erro_import: return None, None, erro_import
        df, error = proc.processar_dados_export_import(dados_export, dados_import, last_updated_month)
        return df, "Série Temporal", error

    elif tipo == "2024":
        dados_export, erro_export = obter_dados_comerciais_ano_anterior(ncm_code, "export", last_updated_month)
        if erro_export: return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais_ano_anterior(ncm_code, "import", last_updated_month)
        if erro_import: return None, None, erro_import
        df, error = proc.processar_dados_ano_anterior(dados_export, dados_import, last_updated_month)
        return df, f"2024 (Até {last_updated_month}/{last_updated_year})", error

    elif tipo == "2025_parcial":
        dados_export, erro_export = obter_dados_comerciais_ano_atual(ncm_code, "export", last_updated_month)
        if erro_export: return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais_ano_atual(ncm_code, "import", last_updated_month)
        if erro_import: return None, None, erro_import
        df, error = proc.processar_dados_ano_atual(dados_export, dados_import, last_updated_month)
        return df, f"2025 (Até {last_updated_month}/{last_updated_year})", error

    else:
        return None, None, "Tipo de período inválido."

def formatar_numero(valor):
    """Formata números para exibição."""
    try:
        return format_decimal(float(valor), format="#,##0.##", locale='pt_BR')
    except (ValueError, TypeError):
        return str(valor)

def exibir_dados(df, periodo, error, resumido=False):
    """Exibe tabelas de dados, com opção de resumo."""
    st.subheader(f"📊 Dados de {periodo}")
    if error:
        st.warning(error)
        return

    if df is None or df.empty:
        st.write("Nenhum dado para exibir.")
        return

    if resumido:
        df = criar_dataframe_resumido(df)
    elif 'year' in df.columns:
        df = df.rename(columns={'year': 'Ano'})

    df_formatado = df.copy()
    if 'Ano' in df_formatado:
        df_formatado['Ano'] = df_formatado['Ano'].astype(str)

    colunas_numericas = [col for col in df_formatado if col != 'Ano']
    df_formatado[colunas_numericas] = df_formatado[colunas_numericas].applymap(formatar_numero)
    st.dataframe(df_formatado)

def exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial, resumido=False):
    """Exibe tabela comparativa entre 2024 e 2025 (mesmo período)."""
    st.subheader("🔄 Comparativo 2024 x 2025 (Mesmo Período)")

    if error_2024 or error_2025_parcial:
        st.warning("Erro: " + (error_2024 or error_2025_parcial))
        return

    if df_2024 is None or df_2024.empty or df_2025_parcial is None or df_2025_parcial.empty:
        st.warning("Não há dados suficientes para comparação.")
        return

    df_comparativo = pd.concat([df_2024, df_2025_parcial], ignore_index=True)
    exibir_dados(df_comparativo, "Comparativo", None, resumido)

def criar_dataframe_resumido(df):
    """Cria DataFrame resumido com colunas selecionadas."""
    if df is None or df.empty: return pd.DataFrame()
    return df[['year', 'Exportações (FOB)', 'Exportações (KG)',
               'Importações (FOB)', 'Importações (KG)',
               'Balança Comercial (FOB)', 'Balança Comercial (KG)']].rename(columns={'year': 'Ano'})

def main():
    st.title("📊 Análise de Comércio Exterior")

    # 1. Obtenção de dados
    last_updated_date, last_updated_year, last_updated_month = obter_data_ultima_atualizacao()
    if last_updated_date == "Erro":
        st.error("❌ Erro ao obter data de atualização.")
        st.stop()
    else:
        st.info(f"📅 Atualizado até: {last_updated_month}/{last_updated_year} ({last_updated_date})")

    ncm_code = st.text_input("Digite o código NCM:")
    if not ncm_code:
        st.stop()

    ncm_formatado = f"{str(ncm_code)[:4]}.{str(ncm_code)[4:6]}.{str(ncm_code)[6:]}"
    st.write(f"📌 NCM selecionado: {ncm_formatado}")

    descricao = obter_descricao_ncm(ncm_code)
    if "Erro" in descricao:
        st.error(descricao)
        return
    st.success(f"📖 Descrição: **{descricao}** (NCM: {ncm_formatado})")

    exibir_resumida = st.checkbox("Exibir tabela resumida")

    df_2025, periodo_2025, error_2025 = obter_e_processar_dados(ncm_code, "2025", last_updated_month, last_updated_year)
    df_2024, periodo_2024, error_2024 = obter_e_processar_dados(ncm_code, "2024", last_updated_month, last_updated_year)
    df_2025_parcial, periodo_2025_parcial, error_2025_parcial = obter_e_processar_dados(ncm_code, "2025_parcial", last_updated_month, last_updated_year)

    # 2. Exibição de dados (tabelas e gráficos)

    # Tabelas
    exibir_dados(df_2025, periodo_2025, error_2025, resumido=exibir_resumida)
    exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial, resumido=exibir_resumida)

    # Download da tabela resumida
    if exibir_resumida:
        if df_2025 is not None and not df_2025.empty:
            df_download = criar_dataframe_resumido(df_2025)
            if df_2024 is not None and not df_2024.empty and df_2025_parcial is not None and not df_2025_parcial.empty:
                df_comparativo_resumido = criar_dataframe_resumido(pd.concat([df_2024, df_2025_parcial]))
                df_download = pd.concat([df_download, df_comparativo_resumido], ignore_index=False)
        elif df_2024 is not None and not df_2024.empty and df_2025_parcial is not None and not df_2025_parcial.empty:
            df_download = criar_dataframe_resumido(pd.concat([df_2024, df_2025_parcial]))
        else:
            df_download = pd.DataFrame()

        if not df_download.empty:
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                df_download.to_excel(writer, sheet_name='Dados Resumidos', index=False)
            excel_file.seek(0)
            st.download_button("📥 Baixar Tabela Resumida (Excel)", excel_file, f"comex_resumido_{ncm_formatado}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Gráficos (KG, FOB e Preço Médio) - Chamadas diretas em main(), com condicionais simples
    if df_2025 is not None and not df_2025.empty:
        st.subheader("📈 Gráfico de Importações (2010-2025) - KG")
        fig_import_kg = graf_kg.gerar_grafico_importacoes(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_import_kg)

        st.subheader("📈 Gráfico de Exportações (2010-2025) - KG")
        fig_export_kg = graf_exp.gerar_grafico_exportacoes(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_export_kg)

        st.subheader("📈 Gráfico de Importações (2010-2025) - US$ FOB")
        fig_import_fob = graf_fob.gerar_grafico_importacoes_fob(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_import_fob)

        st.subheader("📈 Gráfico de Exportações (2010-2025) - US$ FOB")
        fig_export_fob = graf_exp_fob.gerar_grafico_exportacoes_fob(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_export_fob)

        st.subheader("📈 Gráfico de Preço Médio (US$ FOB/KG)")  # Gráfico de Preço Médio
        fig_preco_medio = graf_preco_medio.gerar_grafico_preco_medio(df_2025, df_2024, ncm_formatado)
        st.plotly_chart(fig_preco_medio)

if __name__ == "__main__":
    main()







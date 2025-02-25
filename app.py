import streamlit as st
import pandas as pd
from modulos.api_comex import obter_data_ultima_atualizacao, obter_descricao_ncm, obter_dados_comerciais, obter_dados_comerciais_ano_anterior, obter_dados_comerciais_ano_atual
import modulos.processamento as proc
import locale

# Tentar configurar o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    print("Aviso: Não foi possível configurar o locale para pt_BR.")

def obter_e_processar_dados(ncm_code, tipo, last_updated_month=None, last_updated_year=None):
    """Obtém e processa dados de comércio exterior para um determinado NCM e período."""
    if tipo == "2025":
        dados_export, erro_export = obter_dados_comerciais(ncm_code, "export")
        if erro_export:
            return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais(ncm_code, "import")
        if erro_import:
            return None, None, erro_import
        df, error = proc.processar_dados_export_import(dados_export, dados_import, last_updated_month)
        return df, "Série Temporal", error

    elif tipo == "2024":
        dados_export, erro_export = obter_dados_comerciais_ano_anterior(ncm_code, "export", last_updated_month)
        if erro_export:
            return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais_ano_anterior(ncm_code, "import", last_updated_month)
        if erro_import:
            return None, None, erro_import
        df, error = proc.processar_dados_ano_anterior(dados_export, dados_import, last_updated_month)
        return df, f"2024 (Até {last_updated_month}/{last_updated_year})", error

    elif tipo == "2025_parcial":
        dados_export, erro_export = obter_dados_comerciais_ano_atual(ncm_code, "export", last_updated_month)
        if erro_export:
            return None, None, erro_export
        dados_import, erro_import = obter_dados_comerciais_ano_atual(ncm_code, "import", last_updated_month)
        if erro_import:
            return None, None, erro_import
        df, error = proc.processar_dados_ano_atual(dados_export, dados_import, last_updated_month)
        return df, f"2025 (Até {last_updated_month}/{last_updated_year})", error

    else:
        return None, None, "Tipo de período inválido."

def formatar_numero(valor):
    """Formata um número com separadores de milhar e vírgula para decimal."""
    try:
        valor_float = float(valor)
        if valor_float.is_integer():
            return locale.format_string("%d", valor_float, grouping=True)
        else:
            return locale.format_string("%.2f", valor_float, grouping=True)
    except (ValueError, TypeError):
        return valor

def exibir_dados(df, periodo, error):
    """Exibe os dados no Streamlit, formatando os números."""
    st.subheader(f"📊 Dados de {periodo}")
    if error:
        st.warning(error)
    else:
        if not df.empty:
            df_formatado = df.copy()
            colunas_numericas = [
                'Exportações (FOB)', 'Exportações (KG)', 'Importações (FOB)',
                'Importações (Frete USD)', 'Importações (Seguro USD)',
                'Importações (CIF USD)', 'Importações (KG)',
                'Balança Comercial (FOB)', 'Balança Comercial (KG)',
                'Preço Médio Exportação (US$ FOB/Ton)', 'Preço Médio Importação (US$ FOB/Ton)'
            ]
            for coluna in colunas_numericas:
                if coluna in df_formatado.columns:
                    df_formatado[coluna] = df_formatado[coluna].apply(formatar_numero)
            st.dataframe(df_formatado)
        else:
            st.write("Nenhum dado para exibir.")

def exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial):
    """Exibe o comparativo entre 2024 e 2025 (mesmo período) em uma única tabela."""
    st.subheader("🔄 Comparativo 2024 x 2025 (Mesmo Período)")

    if error_2024 or error_2025_parcial:
        if error_2024:
            st.warning(f"Erro ao obter dados de 2024: {error_2024}")
        if error_2025_parcial:
            st.warning(f"Erro ao obter dados de 2025 (parcial): {error_2025_parcial}")
        return

    if df_2024.empty or df_2025_parcial.empty:
        st.warning("Não há dados suficientes para o comparativo.")
        return

    # Combinar os DataFrames
    df_comparativo = pd.concat([df_2024, df_2025_parcial], ignore_index=True)

    # Formatar números
    df_comparativo_formatado = df_comparativo.copy()
    colunas_numericas = [
        'Exportações (FOB)', 'Exportações (KG)', 'Importações (FOB)',
        'Importações (Frete USD)', 'Importações (Seguro USD)',
        'Importações (CIF USD)', 'Importações (KG)',
        'Balança Comercial (FOB)', 'Balança Comercial (KG)',
        'Preço Médio Exportação (US$ FOB/Ton)',
        'Preço Médio Importação (US$ FOB/Ton)'
    ]
    for coluna in colunas_numericas:
        if coluna in df_comparativo_formatado.columns:
            df_comparativo_formatado[coluna] = df_comparativo_formatado[coluna].apply(formatar_numero)

    st.dataframe(df_comparativo_formatado)

def main():
    st.title("📊 Análise de Comércio Exterior")

    # Obter data da última atualização
    last_updated_date, last_updated_year, last_updated_month = obter_data_ultima_atualizacao()

    if last_updated_date == "Erro":
        st.error("❌ Não foi possível obter a data da última atualização da API.")
    else:
        st.info(f"📅 **Dados atualizados até: {last_updated_month}/{last_updated_year}** ({last_updated_date})")

    # Entrada do usuário para inserir código NCM
    ncm_code = st.text_input("Digite o código NCM:", "")

    if ncm_code:
        # Formatar o NCM com pontos
        ncm_formatado = f"{str(ncm_code)[:4]}.{str(ncm_code)[4:6]}.{str(ncm_code)[6:]}"
        st.write(f"📌 **Código NCM selecionado:** {ncm_formatado}")  # Exibir NCM formatado

        # Buscar a descrição do NCM
        descricao = obter_descricao_ncm(ncm_code)
        if "Erro" in descricao:
            st.error(descricao)
            return
        else:
            st.success(f"📖 Descrição do NCM: **{descricao}** (NCM: {ncm_formatado})")  # Exibir NCM formatado

        # Dados de 2025 (completos) - Série Temporal
        df_2025, periodo_2025, error_2025 = obter_e_processar_dados(ncm_code, "2025", last_updated_month, last_updated_year)
        exibir_dados(df_2025, periodo_2025, error_2025)

        # Comparativo 2024 x 2025 (mesmo período)
        df_2024, _, error_2024 = obter_e_processar_dados(ncm_code, "2024", last_updated_month, last_updated_year)
        df_2025_parcial, _, error_2025_parcial = obter_e_processar_dados(ncm_code, "2025_parcial", last_updated_month, last_updated_year)
        exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial)

if __name__ == "__main__":
    main()






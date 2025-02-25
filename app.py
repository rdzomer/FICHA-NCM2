import streamlit as st
import pandas as pd
from modulos.api_comex import obter_data_ultima_atualizacao, obter_descricao_ncm, obter_dados_comerciais, obter_dados_comerciais_ano_anterior, obter_dados_comerciais_ano_atual
import modulos.processamento as proc
import locale
from io import BytesIO

# Tentar configurar o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')  # Tenta uma alternativa
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
    """Formata um número ou string. Números têm separadores de milhar.
       Strings são retornadas sem modificação.
    """
    try:
        valor_float = float(valor)
        if valor_float.is_integer():
            return locale.format_string("%d", valor_float, grouping=True)
        else:
            return locale.format_string("%.2f", valor_float, grouping=True)
    except (ValueError, TypeError):
        return str(valor)

def exibir_dados(df, periodo, error, resumido=False):
    """Exibe os dados no Streamlit, formatando os números.

    Args:
        df (pd.DataFrame): O DataFrame a ser exibido.
        periodo (str): O período dos dados.
        error (str): Mensagem de erro, se houver.
        resumido (bool): Se True, exibe a versão resumida do DataFrame.
    """
    st.subheader(f"📊 Dados de {periodo}")
    if error:
        st.warning(error)
    else:
        if not df.empty:
            if resumido:
                df = criar_dataframe_resumido(df)
            else:
                # Renomeia 'year' para 'Ano' na tabela *completa*
                if 'year' in df.columns:
                    df = df.rename(columns={'year': 'Ano'})

            df_formatado = df.copy()
            # Garante que a coluna 'Ano' seja do tipo string
            if 'Ano' in df_formatado.columns:
                df_formatado['Ano'] = df_formatado['Ano'].astype(str)

            colunas_numericas = [col for col in df_formatado.columns if col != 'Ano']
            for coluna in colunas_numericas:
                df_formatado[coluna] = df_formatado[coluna].apply(formatar_numero)
            st.dataframe(df_formatado)
        else:
            st.write("Nenhum dado para exibir.")

def exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial, resumido=False):
    """Exibe o comparativo 2024/2025, com opção de tabela resumida."""
    st.subheader("🔄 Comparativo 2024 x 2025 (Mesmo Período)")

    if error_2024 or error_2025_parcial:
        if error_2024:
            st.warning(f"Erro: {error_2024}")
        if error_2025_parcial:
            st.warning(f"Erro: {error_2025_parcial}")
        return

    if df_2024.empty or df_2025_parcial.empty:
        st.warning("Não há dados para comparação.")
        return

    df_comparativo = pd.concat([df_2024, df_2025_parcial], ignore_index=True)

    if resumido:
        df_comparativo = criar_dataframe_resumido(df_comparativo)
    else:
        #Renomeia year para Ano na tabela completa
        if 'year' in df_comparativo.columns:
            df_comparativo = df_comparativo.rename(columns={'year': 'Ano'})

    df_formatado = df_comparativo.copy()

    #Garante que a coluna Ano seja do tipo string
    if 'Ano' in df_formatado.columns:
        df_formatado['Ano'] = df_formatado['Ano'].astype(str)

    colunas_numericas = [col for col in df_formatado.columns if col != 'Ano']
    for coluna in colunas_numericas:
        df_formatado[coluna] = df_formatado[coluna].apply(formatar_numero)

    st.dataframe(df_formatado)

def criar_dataframe_resumido(df):
    """Cria um DataFrame resumido com as colunas especificadas."""
    if df is None or df.empty:
        return pd.DataFrame()
    df_resumido = df[['year', 'Exportações (FOB)', 'Exportações (KG)', 'Importações (FOB)',
                      'Importações (KG)', 'Balança Comercial (FOB)', 'Balança Comercial (KG)']]
    df_resumido = df_resumido.rename(columns={'year': 'Ano'}) #Coluna Ano
    return df_resumido

def main():
    st.title("📊 Análise de Comércio Exterior")

    last_updated_date, last_updated_year, last_updated_month = obter_data_ultima_atualizacao()
    if last_updated_date == "Erro":
        st.error("❌ Erro ao obter data de atualização.")
    else:
        st.info(f"📅 Atualizado até: {last_updated_month}/{last_updated_year} ({last_updated_date})")

    ncm_code = st.text_input("Digite o código NCM:")

    if ncm_code:
        ncm_formatado = f"{str(ncm_code)[:4]}.{str(ncm_code)[4:6]}.{str(ncm_code)[6:]}"
        st.write(f"📌 NCM selecionado: {ncm_formatado}")

        descricao = obter_descricao_ncm(ncm_code)
        if "Erro" in descricao:
            st.error(descricao)
            return
        else:
            st.success(f"📖 Descrição: **{descricao}** (NCM: {ncm_formatado})")

        # Checkbox para tabela resumida
        exibir_resumida = st.checkbox("Exibir tabela resumida")

        # Série Temporal
        df_2025, periodo_2025, error_2025 = obter_e_processar_dados(ncm_code, "2025", last_updated_month, last_updated_year)
        exibir_dados(df_2025, periodo_2025, error_2025, resumido=exibir_resumida)

        # Comparativo
        df_2024, _, error_2024 = obter_e_processar_dados(ncm_code, "2024", last_updated_month, last_updated_year)
        df_2025_parcial, _, error_2025_parcial = obter_e_processar_dados(ncm_code, "2025_parcial", last_updated_month, last_updated_year)
        exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial, resumido=exibir_resumida)

        # Botão de Download (só aparece se a tabela resumida estiver ativada)
        if exibir_resumida:
            if df_2025 is not None and not df_2025.empty and df_2024 is not None and not df_2024.empty and df_2025_parcial is not None and not df_2025_parcial.empty :
                df_download = pd.concat([criar_dataframe_resumido(df_2025), criar_dataframe_resumido(pd.concat([df_2024, df_2025_parcial]))], ignore_index=False)
            elif df_2025 is not None and not df_2025.empty:
                df_download = criar_dataframe_resumido(df_2025)
            elif df_2024 is not None and not df_2024.empty and df_2025_parcial is not None and not df_2025_parcial.empty:
                df_download = criar_dataframe_resumido(pd.concat([df_2024, df_2025_parcial]))
            else:
                df_download = pd.DataFrame()

            if not df_download.empty:
                excel_file = BytesIO()
                with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                    df_download.to_excel(writer, sheet_name='Dados Resumidos', index=False)
                excel_file.seek(0)

                st.download_button(
                    label="📥 Baixar Tabela Resumida (Excel)",
                    data=excel_file,
                    file_name=f"comex_resumido_{ncm_formatado}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()






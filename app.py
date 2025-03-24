import streamlit as st
import pandas as pd
from modulos.api_comex import (
    obter_data_ultima_atualizacao,
    obter_descricao_ncm,
    obter_dados_comerciais,
    obter_dados_comerciais_ano_anterior,
    obter_dados_comerciais_ano_atual
)
import modulos.processamento as proc
import modulos.grafico_importacoes_kg as graf_kg
import modulos.grafico_exportacoes_kg as graf_exp
import modulos.grafico_importacoes_fob as graf_fob
import modulos.grafico_exportacoes_fob as graf_exp_fob
import modulos.grafico_preco_medio_fob as graf_preco_medio
import modulos.resumo_tabelas as resumo_tabelas
from io import BytesIO
from babel.numbers import format_decimal

def formatar_numero(valor):
    try:
        return format_decimal(float(valor), format="#,##0.##", locale='pt_BR')
    except (ValueError, TypeError):
        return str(valor)

def exibir_excel(ncm_code):
    if "df_excel" not in st.session_state or st.session_state.df_excel is None:
        return
    st.subheader("📋 Dados do Excel")
    try:
        resultado_ncm, resultado_entidades = proc.buscar_informacoes_ncm_completo(st.session_state.df_excel, ncm_code)
    except Exception as e:
        st.error(f"Erro ao buscar informações do NCM no Excel: {str(e)}")
        return
    with st.container():
        st.markdown("### Departamento Responsável")
        if not resultado_ncm.empty:
            ncm_info = f"""
            <p>
                <strong>Departamento:</strong> {resultado_ncm.iloc[0].get("Departamento Responsável", "Não disponível")}<br>
                <strong>Coordenação-Geral:</strong> {resultado_ncm.iloc[0].get("Coordenação-Geral Responsável", "Não disponível")}<br>
                <strong>Agrupamento:</strong> {resultado_ncm.iloc[0].get("Agrupamento", "Não disponível")}<br>
                <strong>Setores:</strong> {resultado_ncm.iloc[0].get("Setores", "Não disponível")}<br>
                <strong>Subsetores:</strong> {resultado_ncm.iloc[0].get("Subsetores", "Não disponível")}<br>
                <strong>Produtos:</strong> {resultado_ncm.iloc[0].get("Produtos", "Não disponível")}
            </p>
            """
            st.markdown(ncm_info, unsafe_allow_html=True)
        else:
            st.warning("Informações do NCM não encontradas no Excel.")
    with st.container():
        st.markdown("### Informações das Entidades")
        if not resultado_entidades.empty:
            entidade_info = ""
            for _, row in resultado_entidades.iterrows():
                entidade_info += f"""
                <p>
                    <strong>Sigla:</strong> {row.get('Sigla Entidade', 'Não disponível')}<br>
                    <strong>Nome:</strong> {row.get('Entidade', 'Não disponível')}<br>
                    <strong>Dirigente:</strong> {row.get('Nome do Dirigente', 'Não disponível')}<br>
                    <strong>Cargo:</strong> {row.get('Cargo', 'Não disponível')}<br>
                    <strong>Email:</strong> {f"<a href='mailto:{row.get('E-mail', '')}'>{row.get('E-mail', 'Não disponível')}</a>" if pd.notna(row.get('E-mail', '')) else 'Não disponível'}<br>
                    <strong>Telefone:</strong> {row.get('Telefone', 'Não disponível')}<br>
                    <strong>Celular:</strong> {row.get('Celular', 'Não disponível')}<br>
                    <strong>Contato Importante:</strong> {row.get('Contato Importante', 'Não disponível')}<br>
                    <strong>Cargo (Contato Importante):</strong> {row.get('Cargo (Contato Importante)', 'Não disponível')}<br>
                    <strong>Email (Contato Importante):</strong> {f"<a href='mailto:{row.get('E-mail (Contato Importante)', '')}'>{row.get('E-mail (Contato Importante)', 'Não disponível')}</a>" if pd.notna(row.get('E-mail (Contato Importante)', '')) else 'Não disponível'}<br>
                    <strong>Telefone (Contato Importante):</strong> {row.get('Telefone (Contato Importante)', 'Não disponível')}<br>
                    <strong>Celular (Contato Importante):</strong> {row.get('Celular (Contato Importante)', 'Não disponível')}
                </p>
                <hr>
                """
            st.markdown(entidade_info, unsafe_allow_html=True)
        else:
            st.warning("Não há informações das entidades para este NCM no Excel.")

def exibir_api(ncm_code, last_updated_month, last_updated_year):
    st.subheader("📊 Dados da API e Gráficos")
    exibir_resumida = st.checkbox("Exibir tabela resumida", key="chk_resumido")
    dados_export, dados_import = obter_dados_tuple(ncm_code, "2025", last_updated_month)
    df_2025, error_2025 = proc.processar_dados_export_import(dados_export, dados_import, last_updated_month)
    periodo_2025 = "Série Temporal"
    dados_export, dados_import = obter_dados_tuple(ncm_code, "2024", last_updated_month)
    df_2024, error_2024 = proc.processar_dados_ano_anterior(dados_export, dados_import, last_updated_month)
    periodo_2024 = f"2024 (Até {last_updated_month}/{last_updated_year})"
    dados_export, dados_import = obter_dados_tuple(ncm_code, "2025_parcial", last_updated_month)
    df_2025_parcial, error_2025_parcial = proc.processar_dados_ano_atual(dados_export, dados_import, last_updated_month)
    periodo_2025_parcial = f"2025 (Até {last_updated_month}/{last_updated_year})"
    exibir_dados(df_2025, periodo_2025, error_2025, exibir_resumida)
    exibir_comparativo(df_2024, df_2025_parcial, error_2024, error_2025_parcial, exibir_resumida)
    
    # Exibe os quadros-resumo logo após os dados comparativos
    resumo_tabelas.exibir_resumos()
    
    # Geração dos gráficos
    if df_2025 is not None and not df_2025.empty:
        ncm_formatado = f"{str(ncm_code)[:4]}.{str(ncm_code)[4:6]}.{str(ncm_code)[6:]}"
        st.subheader("📈 Gráfico de Importações (KG)")
        fig_import_kg = graf_kg.gerar_grafico_importacoes(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_import_kg)
        st.subheader("📈 Gráfico de Exportações (KG)")
        fig_export_kg = graf_exp.gerar_grafico_exportacoes(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_export_kg)
        st.subheader("📈 Gráfico de Importações (US$ FOB)")
        fig_import_fob = graf_fob.gerar_grafico_importacoes_fob(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_import_fob)
        st.subheader("📈 Gráfico de Exportações (US$ FOB)")
        fig_export_fob = graf_exp_fob.gerar_grafico_exportacoes_fob(df_2025, df_2024, ncm_formatado, last_updated_month, last_updated_year)
        st.plotly_chart(fig_export_fob)
        st.subheader("📈 Gráfico de Preço Médio (US$ FOB/KG)")
        fig_preco_medio = graf_preco_medio.gerar_grafico_preco_medio(df_2025, df_2024, ncm_formatado, last_updated_month)
        st.plotly_chart(fig_preco_medio)

def obter_dados_tuple(ncm_code, tipo, last_updated_month):
    if tipo == "2025":
        dados_export, _ = obter_dados_comerciais(ncm_code, "export")
        dados_import, _ = obter_dados_comerciais(ncm_code, "import")
    elif tipo == "2024":
        dados_export, _ = obter_dados_comerciais_ano_anterior(ncm_code, "export", last_updated_month)
        dados_import, _ = obter_dados_comerciais_ano_anterior(ncm_code, "import", last_updated_month)
    elif tipo == "2025_parcial":
        dados_export, _ = obter_dados_comerciais_ano_atual(ncm_code, "export", last_updated_month)
        dados_import, _ = obter_dados_comerciais_ano_atual(ncm_code, "import", last_updated_month)
    else:
        dados_export, dados_import = [], []
    return dados_export, dados_import

def exibir_dados(df, periodo, error, resumido=False):
    st.markdown(f"### Dados de {periodo}")
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
    st.markdown("### Comparativo 2024 x 2025 (Mesmo Período)")
    if error_2024 or error_2025_parcial:
        st.warning("Erro: " + (error_2024 or error_2025_parcial))
        return
    if df_2024 is None or df_2024.empty or df_2025_parcial is None or df_2025_parcial.empty:
        st.warning("Não há dados suficientes para comparação.")
        return
    df_comparativo = pd.concat([df_2024, df_2025_parcial], ignore_index=True)
    exibir_dados(df_comparativo, "Comparativo", None, resumido)

def criar_dataframe_resumido(df):
    if df is None or df.empty: 
        return pd.DataFrame()
    return df[['year', 'Exportações (FOB)', 'Exportações (KG)',
               'Importações (FOB)', 'Importações (KG)',
               'Balança Comercial (FOB)', 'Balança Comercial (KG)']].rename(columns={'year': 'Ano'})

def main():
    st.title("📊 Análise de Comércio Exterior")
    last_updated_date, last_updated_year, last_updated_month = obter_data_ultima_atualizacao()
    if last_updated_date == "Erro":
        st.error("❌ Erro ao obter data de atualização.")
        st.stop()
    else:
        st.info(f"📅 Atualizado até: {last_updated_month}/{last_updated_year} ({last_updated_date})")
    uploaded_file = st.file_uploader("Upload do arquivo Excel:", type=["xlsx"])
    if uploaded_file:
        try:
            st.session_state.df_excel = proc.carregar_dados_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao carregar arquivo Excel: {str(e)}")
            st.session_state.df_excel = None
    ncm_code = st.text_input("Digite o código NCM:")
    if not ncm_code:
        st.stop()
    ncm_formatado = f"{str(ncm_code)[:4]}.{str(ncm_code)[4:6]}.{str(ncm_code)[6:]}"
    st.write(f"📌 NCM selecionado: {ncm_formatado}")
    descricao = obter_descricao_ncm(ncm_code)
    if "Erro" in descricao:
        st.error(descricao)
        st.stop()
    st.success(f"📖 Descrição: **{descricao}** (NCM: {ncm_formatado})")
    exibir_excel(ncm_code)
    exibir_api(ncm_code, last_updated_month, last_updated_year)

if __name__ == "__main__":
    main()




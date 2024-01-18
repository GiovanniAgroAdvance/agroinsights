import pandas as pd
import plotly.express as px
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# ... Função display_lead_info ...
def display_lead_info(lead_data):
    with st.expander(f"Dados do Lead: {lead_data['Nome Lead'].iloc[0]}", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Nome:**")
            st.write(lead_data['Nome Lead'].iloc[0])
            st.markdown("**E-mail:**")
            st.write(lead_data['E-mail Lead'].iloc[0])
        with col2:
            st.markdown("**Resumo da ligação:**")
            st.write(lead_data['Resumo'].iloc[0])
        with col3:
            st.markdown("**Cargo:**")
            st.write(lead_data['Cargo'].iloc[0])
            st.markdown("**Desafio:**")
            st.write(lead_data['Desafio'].iloc[0])
            st.markdown("**Link Meetime:**")
            st.write(lead_data['Link Meetime'].iloc[0])

@st.cache_data(ttl=10, hash_funcs={pd.DataFrame: lambda _: None})
def get_data() -> pd.DataFrame:
    # É necessário adicionar tratamento para quando a URL ou o arquivo não está acessível
    try:
        return pd.read_csv(url, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

if __name__ == "__main__":
    st.set_page_config(
        page_title="Ligações Meetime",
        page_icon="logoAgro.png",
        layout="wide",
    )

    # Connect to the Google Sheet
    sheet_id = os.getenv("GOOGLE_sheet_id")
    sheet_name = os.getenv("GOOGLE_sheet_name")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = get_data()

    st.title("📞 Ligações Meetime")

    if df.empty:
        st.stop()  # Para a execução do app se o DataFrame estiver vazio

    # Filtros na barra lateral
    st.sidebar.title("Filtros")

    # Converter a coluna de datas para o tipo datetime
    df['Data'] = pd.to_datetime(df['Data'])

    # Filtros para Data Inicial e Data Final
    min_date = df['Data'].min().date()
    max_date = df['Data'].max().date()
    start_date = st.sidebar.date_input('Data Inicial', max_date)
    end_date = st.sidebar.date_input('Data Final', max_date)
    
    # Atualize a condição do filtro de datas
    df_filtered_by_date = df[(df['Data'].dt.date >= start_date) & (df['Data'].dt.date <= end_date)]



    # Filtro SDR na barra lateral
    sdrs = sorted(pd.unique(df_filtered_by_date["Nome SDR"]))
    selected_sdr = st.sidebar.selectbox("Selecione o SDR", ['Todos'] + sdrs)

    # Aplicar filtro de SDR se necessário
    if selected_sdr != 'Todos':
        df_filtered_by_sdr = df_filtered_by_date[df_filtered_by_date["Nome SDR"] == selected_sdr]
    else:
        df_filtered_by_sdr = df_filtered_by_date
    
    # Display leads se algum SDR foi selecionado
    if not df_filtered_by_sdr.empty:
        leads = sorted(pd.unique(df_filtered_by_sdr["Nome Lead"].dropna()))
        selected_lead = st.sidebar.selectbox("Selecione o Lead", leads)
        df_filtered_by_lead = df_filtered_by_sdr[df_filtered_by_sdr["Nome Lead"] == selected_lead]
        display_lead_info(df_filtered_by_lead)
    else:
        st.sidebar.write("Nenhum dado disponível para o SDR selecionado.")

    # Contagem de ligações por SDR
    count_df = df_filtered_by_date['Nome SDR'].value_counts().reset_index()
    count_df.columns = ['Nome SDR', 'count']

    #fig = px.pie(count_df, names='Nome SDR', values='count', title='Porcentagem de Ligações Significativas Processadas por SDR')
    #st.plotly_chart(fig, use_container_width=True)
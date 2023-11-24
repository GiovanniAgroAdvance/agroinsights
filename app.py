import pandas as pd
import plotly.express as px
import streamlit as st


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
        

def get_data() -> pd.DataFrame:
    return pd.read_csv(url, on_bad_lines='skip')

# Configuração da página
if __name__ == "__main__":
    st.set_page_config(
        page_title="Ligações Meetime",
        page_icon="logoAgro.png",
        layout="wide",
    )

    # Connect to the Google Sheet
    sheet_id = "1dJmgQM0P2a3VYBUR1gPjbm2qtLe5KxkAra3HbCx4Hnk"
    sheet_name = "databaseTeste"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url, dtype=str).fillna("")

    st.title("Ligações Meetime")

    # Ordenar os nomes dos SDRs em ordem alfabética antes de passá-los para o selectbox
    sdrs = sorted(pd.unique(df["Nome SDR"]))
    selected_sdr = st.sidebar.selectbox("Selecione o SDR", sdrs)
    df_filtered_by_sdr = df[df["Nome SDR"] == selected_sdr]

    if not df_filtered_by_sdr.empty:
        # Ordenar os nomes dos Leads em ordem alfabética antes de passá-los para o selectbox
        leads = sorted(pd.unique(df_filtered_by_sdr["Nome Lead"]))
        selected_lead = st.sidebar.selectbox("Selecione o Lead", leads)
        df_filtered_by_lead = df_filtered_by_sdr[df_filtered_by_sdr["Nome Lead"] == selected_lead]

        display_lead_info(df_filtered_by_lead)
    else:
        st.write("Nenhum dado disponível para o SDR selecionado.")

    count_df = df['Nome SDR'].value_counts().reset_index()
    count_df.columns = ['Nome SDR', 'count']

    fig = px.pie(count_df, names='Nome SDR', values='count', title='Porcentagem de Ligações por SDR')
    st.plotly_chart(fig, use_container_width=True)
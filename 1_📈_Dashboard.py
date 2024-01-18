import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

# Função para obter os registros da API
def obter_registros(data_formatada):
    base_url = "https://api.meetime.com.br/v2/calls"
    headers = {
        "accept": "application/json",
        "Authorization": os.getenv("MEETIME_Authorization"),
        "Ocp-Apim-Subscription-Key": os.getenv("MEETIME_Ocp_Apim_Subscription_Key")
    }
    limit = 100
    start = 0
    todos_os_registros = []

    while True:
        url = f"{base_url}?limit={limit}&start={start}&started_after={data_formatada}"
        response = requests.get(url, headers=headers)
        data = response.json()
        todos_os_registros.extend(data["data"])

        if len(data["data"]) < limit:
            break
        else:
            start += limit

    return todos_os_registros

# Função para contagem de ligações por categoria e por usuário
# Função para contagem de ligações por categoria e por usuário
# Função para contagem de ligações por categoria e por usuário
def contar_ligacoes_por_categoria_e_usuario(registros):
    mapeamento_categorias = {
        "NO_CONTACT": "SEM_CONTATO",
        "MEANINGFUL": "SIGNIFICATIVO",
        "NOT_MEANINGFUL": "NAO_SIGNIFICATIVO",
        "CLIENT_BUSY": "CLIENTE_OCUPADO",
        "NOT_PERFORMED": "NAO_REALIZADO"
    }

    output_dict_categoria = {
        "SEM_CONTATO": 0,
        "SIGNIFICATIVO": 0,
        "NAO_SIGNIFICATIVO": 0,
        "CLIENTE_OCUPADO": 0,
        "NAO_REALIZADO": 0
    }

    output_dict_usuario = {}

    for registro in registros:
        output = registro.get("output")
        output2 = registro.get("status")
        usuario_nome = registro.get("user_name")

        if output2 == "CONNECTED" and output in mapeamento_categorias:
            output_portugues = mapeamento_categorias[output]
        
            # Contagem por categoria
            output_dict_categoria[output_portugues] += 1

            # Contagem por usuário
            if usuario_nome in output_dict_usuario:
                # Se o usuário já existe, verifique se a categoria já existe no dicionário para o usuário
                if output_portugues in output_dict_usuario[usuario_nome]:
                    output_dict_usuario[usuario_nome][output_portugues] += 1
                else:
                    output_dict_usuario[usuario_nome][output_portugues] = 1
            else:
                # Se o usuário ainda não existe, inicialize o dicionário para o usuário
                output_dict_usuario[usuario_nome] = {output_portugues: 1}
        
        elif output2 == "NOT_PERFORMED":
            output_dict_categoria["NAO_REALIZADO"] += 1

    return output_dict_categoria, output_dict_usuario


def criar_graficos(dados):
    fig = go.Figure()

    color_dict = {}  # armazena a cor associada a cada rótulo
    colors = px.colors.qualitative.Plotly  # defina a paleta de cores

    categorias = set()

    for i, (usuario_nome, contador_de_categoria) in enumerate(sorted(dados.items())): 
        color_dict[usuario_nome] = colors[i % len(colors)]  # associar cor a cada rótulo único

    # ordena o dicionário de cores alfabeticamente pelo nome do usuário
    color_dict = dict(sorted(color_dict.items(), key=lambda item: item[0]))

    for usuario_nome, color in color_dict.items():
        contador_de_categoria = dados.get(usuario_nome, {})
        x_values = list(contador_de_categoria.keys())
        categorias.update(x_values)

        for categoria in x_values:
            quantidade = contador_de_categoria.get(categoria, 0)
            fig.add_trace(go.Bar(
                x=[categoria],
                y=[quantidade],
                marker_color=color,
                text=f'{usuario_nome}: {quantidade}',
                name=f'{usuario_nome}',
                legendgroup=f'{usuario_nome}',  # adicionamos esta linha
                hoverinfo='y+name'
            ))

    # Adicionando o menu drop-down
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=["visible", [categoria in trace["x"][0] for trace in fig["data"]]],
                        label="Todas",
                        method="restyle"
                    )] +
                    [
                        dict(
                            args=["visible", [categoria == trace["x"][0] for trace in fig["data"]]],
                            label=categoria,
                            method="restyle"
                        )
                        for categoria in categorias
                    ]
                ),
            )
        ],

        barmode='stack',
        xaxis=dict(title='CATEGORIA', showgrid=False),
        yaxis=dict(title='TOTAL LIGAÇÕES', showgrid=False),
        title='Desempenho dos SDRs por Categoria de Ligações',
        showlegend=False,
    )

    total = sum(sum(contador_de_categoria.values()) for contador_de_categoria in dados.values())
    labels_values = sorted([(usuario_nome, sum(contador_de_categoria.values()) * 100 / total) for usuario_nome, contador_de_categoria in dados.items()])
    labels = [item[0] for item in labels_values]
    values = [item[1] for item in labels_values]

    fig_pizza = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=[color_dict.get(label, "#000") for label in labels])])
    fig_pizza.update_layout(title_text="Proporção de Ligações por SDR")

    return fig, fig_pizza



# Função principal do Streamlit
def main():
    st.set_page_config(
        page_title="Ligações Meetime",
        page_icon="logoAgro.png",
        layout="wide",
    )
    
    st.title("📈DASHBOARD")

    # Defina a data para o dia desejado
    data_formatada = datetime.now().strftime("%Y-%m-%d")

    # Adicione um spinner de carregamento durante a obtenção dos dados
    with st.spinner("Carregando dados..."):
        # Obtenha os registros da API
        registros = obter_registros(data_formatada)

    # Conte as ligações por categoria e por usuário
    ligacoes_por_categoria, ligacoes_por_usuario = contar_ligacoes_por_categoria_e_usuario(registros)

    # Mostre os resultados na dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="SIGNIFICATIVAS:", value=ligacoes_por_categoria['SIGNIFICATIVO'])
    col2.metric(label="NÃO SIGNIFICATIVAS:", value=ligacoes_por_categoria['NAO_SIGNIFICATIVO'])
    col3.metric(label="SEM CONTATO:", value=ligacoes_por_categoria['SEM_CONTATO'])
    col4.metric(label="CLIENTE OCUPADO:", value=ligacoes_por_categoria['CLIENTE_OCUPADO'])
    col5.metric(label="NÃO CONECTADA:", value=ligacoes_por_categoria['NAO_REALIZADO'])


    # Dados do desempenho dos usuários
    dados_usuarios = {}

    # Obtenha os dados do desempenho dos usuários e atribua diretamente à variável dados_usuarios
    for usuario_nome, contagem_por_categoria in ligacoes_por_usuario.items():
        dados_usuarios[f'{usuario_nome}'] = contagem_por_categoria

    ordem_categorias = ['SIGNIFICATIVO', 'NAO_SIGNIFICATIVO', 'SEM_CONTATO', 'CLIENTE_OCUPADO', 'NAO_REALIZADO']
    categorias_unicas = sorted(set(categoria for contagem_por_categoria in dados_usuarios.values() for categoria in contagem_por_categoria), key=ordem_categorias.index)

    # Adicione um gráfico de linhas interativo à interface do Streamlit
    if dados_usuarios:
        fig_barras, fig_pizza = criar_graficos(dados_usuarios)

        # Adicione o gráfico de pizza ao lado do gráfico de barras
        #col1, col2 = st.columns(2)
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.warning("Nenhum dado de desempenho dos usuários disponível.")



if __name__ == "__main__":
    main()

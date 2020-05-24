import streamlit as st 
import pandas as pd 
import sqlite3
import time
import os
import webbrowser
from model import pipeline_model

#DB
conn = sqlite3.connect('enderecos.db')
c = conn.cursor()

#SQL Functions
def drop_table():
    c.execute("DROP TABLE IF EXISTS enderecostable")

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS enderecostable (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, categoria TEXT, endereco TEXT,loja TEXT)")

def create_data(category, address, shop=None, id = None):
    c.execute("INSERT INTO enderecostable(id, categoria, endereco, loja) VALUES (?, ?, ?, ?)", (id, category, address, shop))
    conn.commit()

def view_all_rows():
    c.execute("SELECT * FROM enderecostable")
    data = c.fetchall()
    return data

def view_origin():
    c.execute("SELECT endereco FROM enderecostable WHERE categoria = 'origem'")
    data = c.fetchall()
    return data

def view_shops():
    c.execute("SELECT endereco,loja FROM enderecostable WHERE categoria = 'loja'")
    data = c.fetchall()
    return data

def view_addresses():
    c.execute("SELECT endereco, loja FROM enderecostable WHERE categoria = 'entrega'")
    data = c.fetchall()
    return data

def view_rows_by_category(category):
    c.execute("SELECT * FROM enderecostable WHERE categoria = '{}'".format(category))
    data = c.fetchall()
    return data

def delete_origin():
    c.execute("DELETE FROM enderecostable WHERE categoria = 'origem'")
    conn.commit()

def delete_data_by_address(address):
    c.execute("DELETE FROM enderecostable WHERE endereco='{}'".format(address))
    conn.commit()

def delete_data_by_shop(shop):
    c.execute('DELETE FROM enderecostable WHERE loja="{}"'.format(shop))
    conn.commit()

def get_address_by_id(id):
    c.execute("SELECT * FROM enderecostable WHERE id = {}".format(id))
    data = c.fetchall()
    return data


#MODEL Function
def run_model(addresses, shops_names, metric):
    time.sleep(1)
    st.success('Sucesso! Seu mapa está sendo gerado...')
    n_shops = len(set(shops_names))
    # time.sleep(1)
    # st.success('Carregando...')
    st.markdown("""
    <h3>Legenda:</h3>
    <ul style="list-style-type:none;">
        <li><span style="color:black;font-weight:bold;">Preto</span> - Endereço de origem</li>
        <li><span style="color:#2ca02c;font-weight:bold;">Verde</span> - Lojas</li>
        <li><span style="color:#BA3CC2;font-weight:bold;">Lilás</span> - Entregas</li>
    </ul>
    """, unsafe_allow_html=True)

    route_map = pipeline_model(addresses, shops_names, n_shops, metric)
    #st.markdown(route_map.render(), unsafe_allow_html=True)
    filepath = os.path.realpath('map.html')
    route_map.save(filepath)

    st.markdown("""
    <iframe src='http://127.0.0.1:5000/map' width=700 height=500></iframe>
    """, unsafe_allow_html=True)
    # st.markdown(route_map)
    # st.markdown(route_map._repr_html_(), unsafe_allow_html=True)
    #webbrowser.open('file://' + filepath)


def main():
    st.title('HACKINGHELP 2020 - Equipe Minervianos')
    menu = ['Explicação', 'App']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Explicação':
        st.image(['./img/002minerva_color_hor.png', './img/5eb0e201e2149.jpg'], width=200)
        #Insira a explicação do app aqui
        st.header("Evolution Router App")
        st.markdown("""
        <div>
            <h3>Apresentação</h3>
            <p>O  Evolution Router é um web app que visa roteirizar e otimizar o sistema de entregas de empresas a partir de um pool system. Nesse sentido, buscamos ajudar as micro e pequenas empresas, visto que é um setor que encontrou problemas de adaptação de funcionamento com o cenário da pandemia.</p>
            <h3>Produto</h3>
            <p>O projeto visa melhorar a eficiência operacional das entregas, focando nas métricas de custo operacional e tempo de entrega. Usamos inteligência artificial para definir as rotas mais rápidas entre os pontos, levando em conta o tráfego em tempo real - o que pode diminuir aglomeração em tempos de COVID-19 e diminuir o tempo de entrega - e depois otimizamos a rota baseado na menor distância total percorrida por essas rotas mais rápidas - diminuindo assim os custos por combustível e manutenção de veículos. A otimização também pode ser flexibilizada tanto por Entrega Mais Rápida quanto Entrega Mais Curta, podendo ser optada pela preferência do cliente.</p>
            <p>As entregas são feitas por um pool system, no qual o entregador retira primeiramente os itens nas empresas e em seguida segue em direção aos clientes,  se adequando a melhor rota para ambas as situações. Esse sistema permite que haja redução de custos e melhore a eficiência o operacional de entregas.</p>
            <p>O produto tem o intuito de ajudar as microempresas que representam um total de 99% do setor privado, responsável por boa parte da movimentação da  economia brasileira e a maior geração de empregos, que no cenário atual está sendo muito afetado.</p>
            <h3>Informações adicionais</h3>
            <p>Nesse projeto, foi utilizada a linguagem de programação Python. A sua facilidade de escrever, além da vasta quantidade de bibliotecas fornecidas pela comunidade, faz com que o Python seja uma ferramenta poderosa para integrar as tecnologias utilizadas. Dois frameworks dessa linguagem foram usados para facilitar o desenvolvimento da aplicação: Streamlit e Flask.</p>
            <p>A API de geolocalização utilizada foi a Nominatim, fornecida pela biblioteca geopy, no Python. Com ela, é possível conseguir resultados relativamente precisos de latitude e longitude, apenas digitando o endereço desejado.</p>
            <p>Já a API de tráfego em tempo real utilizada, foi a fornecida pela <a href="https://www.here.com/" target="_blank">HERE</a>. Com ela, é possível realizar requisições REST de forma gratuita e ainda fornece diversos parâmetros de busca.<p>
            <p>O algoritmo de inteligência artificial utilizado foi o algoritmo genético. Ele foi adaptado desse <a href="https://github.com/ZWMiller/PythonProjects/blob/master/genetic_algorithms/evolutionary_algorithm_traveling_salesman.ipynb" target="_blank">repositório GitHub</a>. A cada população gerada pelo algoritmo, mais refinado é o resultado.</p>
            <p>Por último, o mapa gerado é resultado da utilização da biblioteca Folium. Com ela, é possível adicionar popups, tooltips e markers, deixando o mapa mais interativo.</p>
            <p><a href="https://youtu.be/K7dWKXp45Xg" target="_blank">Vídeo de demonstração web app</a></p>
            <p>Contato técnico: <a href="mailto:henriquechavesmm@gmail.com">henriquechavesmm@gmail.com</a></p>

        """, unsafe_allow_html = True)
        
    
    elif choice == 'App':
        st.header("Evolution Router App")
        app_sections = ['Cadastrar Origem', 'Cadastrar Loja', 'Cadastrar Entrega', 'Gerenciar Endereços', 'Gerar Rota']
        applist = st.sidebar.selectbox("Funções do App", app_sections)
        
        if applist == 'Cadastrar Origem':
            st.subheader('Cadastrar endereço de origem')
            st.warning("Ao cadastrar um novo endereço de origem, o antigo será removido.")
            origem_endereco_input = st.text_input("Insira o endereço de origem:")

            if st.button("Adicionar origem"):
                #drop_table()
                create_table()
                if view_origin():
                    delete_origin()
                create_data('origem', origem_endereco_input, None)
                    
                st.success('Origem adicionada com sucesso.')

        elif applist == 'Cadastrar Loja':
            st.subheader('Cadastrar endereço de loja')

            loja_loja_input = st.text_input("Digite o nome da loja:")
            loja_endereco_input = st.text_input("Insira o endereço da loja:")
            
            if st.button("Adicionar loja"):
                create_data('loja', loja_endereco_input, shop=loja_loja_input)
                st.success('Loja adicionada com sucesso.')

        elif applist == 'Cadastrar Entrega':
            st.subheader('Cadastrar endereço de entrega')
            lista_nomes_lojas = [i[1] for i in view_shops()]
            entrega_loja_input = st.selectbox("Escolha a loja vendedora:", lista_nomes_lojas)
            entrega_endereco_input = st.text_input("Insira o endereço de entrega:")
            if st.button("Adicionar entrega"):
                create_data('entrega', entrega_endereco_input, entrega_loja_input)
                st.success('Endereço de entrega adicionado com sucesso.')
                time.sleep(1)
                st.write('Adicione mais endereços de entrega caso queira aumentar sua rota de entrega.')
        
        elif applist == 'Gerenciar Endereços':
            st.subheader('Visualizar informações referentes à sua rota')
            info_choice = st.radio("Visualizar: ", ("origem", "loja", "entrega"))

            if info_choice == 'origem':
                st.dataframe(pd.DataFrame({'Endereço da origem':view_origin()[0]}))
            
            elif info_choice == 'loja':
                lojas_nomes = [i[1] for i in view_shops()]
                lojas_enderecos = [i[0] for i in view_shops()]
                st.dataframe(pd.DataFrame({'Nome da loja':lojas_nomes, 'Endereço da loja':lojas_enderecos}))

                loja_a_excluir = st.selectbox("Excluir uma loja:", lojas_nomes)
                if st.button("Excluir"):
                    delete_data_by_shop(loja_a_excluir)
                    st.warning("{} foi excluída.".format(loja_a_excluir))
                if st.button("Excluir todas as lojas"):
                    for loja in lojas_nomes:
                        delete_data_by_shop(loja)
                    st.warning("Todas as lojas foram excluídas.")
            
            elif info_choice == 'entrega':
                entregas_enderecos = [i[0] for i in view_addresses()]
                entregas_lojas = [i[1] for i in view_addresses()]
                st.dataframe(pd.DataFrame({'Endereço de entrega': entregas_enderecos, 'Loja vendedora': entregas_lojas}))

                entrega_a_excluir = st.selectbox("Excluir uma entrega:", entregas_enderecos)
                if st.button("Excluir"):
                    delete_data_by_address(entrega_a_excluir)
                    st.warning("Entrega excluída: '{}'.".format(entrega_a_excluir))
                if st.button("Excluir todas as entregas"):
                    for endereco in entregas_enderecos:
                        delete_data_by_address(endereco)
                    st.warning("Todos os endereços de entrega foram excluídos.")
   

        elif applist == 'Gerar Rota':
            st.subheader('Gere sua rota otimizada baseada nos endereços registrados')
            metrica_radio = st.radio("Seleciona a métrica de otimização: ", ("distância total", "tempo total"))
            metrica = 'distance'
            if metrica_radio == 'distância total':
                    metrica = 'distance'
            elif metrica_radio == 'tempo total':
                    metrica = 'time'

            if st.button("Gerar rota"):
                colunas = ['Id', 'Categoria', 'Endereco', 'Loja']
                df_origem = pd.DataFrame(view_rows_by_category('origem'), columns=colunas)
                df_lojas = pd.DataFrame(view_rows_by_category('loja'), columns=colunas)
                df_entregas = pd.DataFrame(view_rows_by_category('entrega'), columns=colunas)

                enderecos_model = [*df_origem['Endereco'], *df_lojas['Endereco'], *df_entregas['Endereco']]
                nome_lojas_model = [*df_lojas['Loja'], *df_entregas['Loja']]
                
                run_model(enderecos_model, nome_lojas_model, metrica)





if __name__ == '__main__':
    main()
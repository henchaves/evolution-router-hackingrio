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
    c.execute('DROP TABLE IF EXISTS enderecostable')

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS enderecostable (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
                                                          endereco TEXT)')

def create_data(address):
    c.execute('INSERT INTO enderecostable(id, endereco) VALUES (?, ?)',(None, address))
    conn.commit()

def view_all_rows():
    c.execute('SELECT * FROM enderecostable')
    data = c.fetchall()
    return data

def view_origin():
    c.execute('SELECT endereco FROM enderecostable WHERE id = 1')
    data = c.fetchall()
    return data

def view_addresses():
    c.execute('SELECT endereco FROM enderecostable WHERE id != 1')
    data = c.fetchall()
    return data

#MODEL Function
def run_model(addresses, metric):
    st.write('Carregando...')
    route_map = pipeline_model(addresses, metric)
    filepath = os.path.realpath('map.html')
    route_map.save(filepath)
    webbrowser.open('file://' + filepath)


def main():
    st.title('HACKINGHELP 2020 - Equipe Minervianos')
    menu = ['Explicação', 'App']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Explicação':
        #Insira a explicação do app aqui
        st.subheader("Evolution Router App")
        st.markdown('Explicação aqui.')

        st.markdown("""
        <div>
            <p>O nosso projeto visa melhorar a eficiência operacional das entregas, focando nas métricas de custo operacional e tempo de entrega.</p>
            <p>Usamos inteligência artificial para definir as rotas mais rápidas entre os pontos, levando em conta o tráfego em tempo real - o que pode diminuir aglomeração em tempos de COVID-19 e diminuir o tempo de entrega - e depois otimizamos a rota baseado na menor distância total percorrida por essas rotas mais rápidas - diminuindo assim os custos por combustível e manutenção de veículos.</p>
            <p>A otimização também pode ser flexibilizada tanto por Entrega Mais Rápida quanto Entrega Mais Curta, podendo ser optada pela preferência do cliente.</p>
            <p>Dessa forma, de forma ideal podemos unir uma comunidade juntando empresas de Rotas como Waze, empresas de Entregas como Correios, empresas de Delivery como iFood e tudo isso utilizando uma inteligência artificial que utiliza dados em tempo real.</p>
        </div>
        """, unsafe_allow_html = True)
        #
    
    elif choice == 'App':
        st.subheader("Evolution Router App")
        app_sections = ['Cadastrar Origem', 'Cadastrar Entrega', 'Visualizar Informações', 'Gerar Rota']
        applist = st.sidebar.selectbox("Funções do App", app_sections)
        
        if applist == 'Cadastrar Origem':
            st.subheader('Cadastrar endereço de origem')
            st.warning("Ao cadastrar um novo endereço de origem, os endereços de entrega em sua rota serão excluídos.")
            origem = st.text_input("Insira o endereço de origem.")

            if st.button("Adicionar origem"):
                drop_table()
                create_table()
                create_data(origem)
                st.success('Origem adicionada com sucesso.')

        elif applist == 'Cadastrar Entrega':
            st.subheader('Cadastrar endereço de entrega')

            entrega = st.text_input("Insira o endereço de entrega.")
            if st.button("Adicionar endereço"):
                create_data(entrega)
                st.success('Endereço adicionado com sucesso.')
                time.sleep(2)
                st.write('Adicione mais endereços de entrega caso queira aumentar sua rota de entrega.')
        
        elif applist == 'Visualizar Informações':
            st.subheader('Visualizar informações referentes à sua rota')
            info_choice = st.radio("Visualizar endereço(s): ", ("origem", "entregas"))

            if info_choice == 'origem':
                st.dataframe(pd.DataFrame({'origem':view_origin()[0]}))
            
            elif info_choice == 'entregas':
                st.dataframe(pd.DataFrame({'entregas': [i[0] for i in view_addresses()]}))
   

        elif applist == 'Gerar Rota':
            st.subheader('Gere sua rota otimizada baseada nos endereços registrados')
            metric_radio = st.radio("Seleciona a métrica de otimização: ", ("distância total", "tempo total"))
            metric = NotImplementedError
            if metric_radio == 'distância total':
                    metric = 'distance'
            elif metric_radio == 'tempo total':
                    metric = 'time'
            if st.button("Gerar rota") and metric is not None:
                result = view_all_rows()
                clean_db = pd.DataFrame(result, columns=['Id', 'Enderecos'])
                enderecos = clean_db['Enderecos']
                
                run_model(enderecos, metric)





if __name__ == '__main__':
    main()
import streamlit as st 
import pandas as pd 
import sqlite3
import time
from model import pipeline_model
import os
import webbrowser

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
def run_model(addresses):
    st.write('Carregando...')
    route_map = pipeline_model(addresses)
    #st.markdown(route_map.get_root().render, unsafe_allow_html=True)
    #C:/Users/T-Gamer/Desktop/hackingrio/code/map.html"
    #st.markdown('<iframe width="800px" height="900px" src="C:/Users/T-Gamer/Desktop/hackingrio/code/map.html"></iframe>', unsafe_allow_html=True)
    
    #filepath = 'C:/Users/T-Gamer/Desktop/hackingrio/code/map.html'
    filepath = os.path.realpath('map.html')
    route_map.save(filepath)
    webbrowser.open('file://' + filepath)
    #st.markdown('<iframe width="560" height="315" src="{}\map.html"></iframe>'.format(x), unsafe_allow_html=True)


def main():
    st.title('HACKINGHELP 2020 - Equipe Minervianos')
    menu = ['Explicação', 'App']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Explicação':
        #Insira a explicação do app aqui
        st.subheader("Evolution Router App")
        st.markdown('Explicação aqui.')
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
                st.write([i[0] for i in view_origin()])
            
            elif info_choice == 'entregas':
                st.write([i[0] for i in view_addresses()])
   

        elif applist == 'Gerar Rota':
            st.subheader('Gere sua rota otimizada baseada nos endereços registrados')
            if st.button("Gerar rota"):
                result = view_all_rows()
                clean_db = pd.DataFrame(result, columns=['Id', 'Enderecos'])
                enderecos = clean_db['Enderecos']
                run_model(enderecos)





if __name__ == '__main__':
    main()
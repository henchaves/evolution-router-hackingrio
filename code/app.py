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

def create_data(address, id = None):
    c.execute('INSERT INTO enderecostable(id, endereco) VALUES (?, ?)',(id, address))
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

def delete_origin():
    c.execute('DELETE FROM enderecostable WHERE id=1')
    conn.commit()

def delete_address(address):
    c.execute('DELETE FROM enderecostable WHERE endereco="{}"'.format(address))
    conn.commit()

def get_address_by_id(id):
    c.execute('SELECT * FROM enderecostable WHERE id = {}'.format(id))
    data = c.fetchall()
    return data

# def update_origin(address):
#     c.execute('UPDATE enderecostable SET endereco="{}" WHERE id=1'.format(address))
#     conn.commit()
#MODEL Function
def run_model(addresses, metric):
    time.sleep(1)
    st.success('Carregando...')
    st.markdown("""
    <h3>Legenda:</h3>
    <ul style="list-style-type:none;">
        <li><span style="color:black;margin-left:0;padding-left:0;">Preto</span> - Endereço de origem</li>
        <li><span style="color:green;">Verde</span> - Primeira entrega</li>
        <li><span style="color:red;">Vermelho</span> - Última entrega</li>
        <li><span style="color:blue;">Azul</span> - Demais entregas</li>
    </ul>
    """, unsafe_allow_html=True)
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
        st.markdown("""
        <div>
            <p>O nosso projeto visa melhorar a eficiência operacional das entregas, focando nas métricas de custo operacional e tempo de entrega.</p>
            <p>Usamos inteligência artificial para definir as rotas mais rápidas entre os pontos, levando em conta o tráfego em tempo real - o que pode diminuir aglomeração em tempos de COVID-19 e diminuir o tempo de entrega - e depois otimizamos a rota baseado na menor distância total percorrida por essas rotas mais rápidas - diminuindo assim os custos por combustível e manutenção de veículos.</p>
            <p>A otimização também pode ser flexibilizada tanto por Entrega Mais Rápida quanto Entrega Mais Curta, podendo ser optada pela preferência do cliente.</p>
            <p>Dessa forma, de forma ideal podemos unir uma comunidade juntando empresas de Rotas como Waze, empresas de Entregas como Correios, empresas de Delivery como iFood e tudo isso utilizando uma inteligência artificial que utiliza dados em tempo real.</p>
        </div>
        """, unsafe_allow_html = True)
        
    
    elif choice == 'App':
        st.subheader("Evolution Router App")
        app_sections = ['Cadastrar Origem', 'Cadastrar Entrega', 'Visualizar Informações', 'Gerar Rota']
        applist = st.sidebar.selectbox("Funções do App", app_sections)
        
        if applist == 'Cadastrar Origem':
            st.subheader('Cadastrar endereço de origem')
            st.warning("Ao cadastrar um novo endereço de origem, o antigo será atualizado.")
            origem = st.text_input("Insira o endereço de origem:")

            if st.button("Adicionar origem"):
                #drop_table()
                create_table()
                if get_address_by_id(1):
                    delete_origin()
                    create_data(origem, id=1)
                else:
                    create_data(origem)
                    
                st.success('Origem adicionada com sucesso.')

        elif applist == 'Cadastrar Entrega':
            st.subheader('Cadastrar endereço de entrega')

            entrega = st.text_input("Insira o endereço de entrega:")
            if st.button("Adicionar entrega"):
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
                all_addresses = [i[0] for i in view_addresses()]
                st.dataframe(pd.DataFrame({'entregas': all_addresses}))
                address_to_del = st.selectbox("Excluir um endereço:", all_addresses)
                if st.button("Excluir"):
                    delete_address(address_to_del)
                    st.warning("Endereço excluído: '{}'".format(address_to_del))
                if st.button("Excluir todos"):
                    for i in all_addresses:
                        delete_address(i)
                    st.warning("Todos os endereços foram excluídos.")
   

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
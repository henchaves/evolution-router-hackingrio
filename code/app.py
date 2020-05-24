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

# def update_origin(address):
#     c.execute('UPDATE enderecostable SET endereco="{}" WHERE id=1'.format(address))
#     conn.commit()


#MODEL Function
def run_model(addresses, shops_names, metric):
    time.sleep(1)
    st.success('Carregando...')
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
                    st.warning("Todos os endereços foram excluídos.")
   

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
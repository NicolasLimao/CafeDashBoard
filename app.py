import streamlit as st
import pandas as pd
import os 
from datetime import datetime

CLIENTES_FILE = 'clientes.csv'
VENDAS_FILE = 'vendas.csv'
PRODUTOS_FILE = 'produtos.csv'

# Verifica se os arquivos CSV existem, caso contrário, cria-os com as colunas apropriadas
if not os.path.exists(CLIENTES_FILE):
    pd.DataFrame(columns=['id', 'nome', 'telefone']).to_csv(CLIENTES_FILE, index=False)

if not os.path.exists(VENDAS_FILE):
    pd.DataFrame(columns=['cliente_id', 'produto', 'quantidade', 'data']).to_csv(VENDAS_FILE, index=False)

if not os.path.exists(PRODUTOS_FILE):
    pd.DataFrame(columns=['id', 'nome', 'preco']).to_csv(PRODUTOS_FILE, index=False)

# Funções para carregar e salvar dados
def carregar_clientes():
    if os.path.getsize(CLIENTES_FILE) == 0:
        return pd.DataFrame(columns=["id", "nome", "telefone"])
    return pd.read_csv(CLIENTES_FILE)

def carregar_vendas():
    if os.path.getsize(VENDAS_FILE) == 0:
        return pd.DataFrame(columns=["cliente_id", "produto", "quantidade", "data"])
    return pd.read_csv(VENDAS_FILE)

def carregar_produtos():
    if os.path.getsize(PRODUTOS_FILE) == 0:
        return pd.DataFrame(columns=["id", "nome", "preco"])
    return pd.read_csv(PRODUTOS_FILE)

def salvar_cliente(nome, telefone):
    df = carregar_clientes()
    novo_id = df['id'].max() + 1 if not df.empty else 1
    novo_cliente = pd.DataFrame({'id': [novo_id], 'nome': [nome], 'telefone': [telefone]})
    df = pd.concat([df, novo_cliente])
    df.to_csv(CLIENTES_FILE, index=False)

def salvar_venda(cliente_id, produto, quantidade):
    df = carregar_vendas()
    nova_venda = pd.DataFrame([[cliente_id, produto, quantidade, datetime.today().strftime('%Y-%m-%d')]],
                               columns=['cliente_id', 'produto', 'quantidade', 'data'])
    df = pd.concat([df, nova_venda])
    df.to_csv(VENDAS_FILE, index=False)

def salvar_produto(nome, preco):
    df = carregar_produtos()
    novo_id = df['id'].max() + 1 if not df.empty else 1
    novo_produto = pd.DataFrame({'id': [novo_id], 'nome': [nome], 'preco': [preco]})
    df = pd.concat([df, novo_produto])
    df.to_csv(PRODUTOS_FILE, index=False)
    
def excluir_produto(produto_id):
    df = carregar_produtos()
    df = df[df['id'] != produto_id]
    df.to_csv(PRODUTOS_FILE, index=False)

def editar_produto(produto_id, novo_nome, novo_preco):
    df = carregar_produtos()
    df.loc[df['id'] == produto_id, ['nome', 'preco']] = [novo_nome, novo_preco]
    df.to_csv(PRODUTOS_FILE, index=False)

def listar_clientes():
    df = carregar_clientes()
    if df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        st.dataframe(df.rename(columns={"id": "ID", "nome": "Nome", "telefone": "Telefone"}))

def excluir_cliente(cliente_id):
    df = carregar_clientes()
    df = df[df['id'] != cliente_id]
    df.to_csv(CLIENTES_FILE, index=False)

def editar_cliente(cliente_id, novo_nome, novo_telefone):
    df = carregar_clientes()
    df.loc[df['id'] == cliente_id, ['nome', 'telefone']] = [novo_nome, novo_telefone]
    df.to_csv(CLIENTES_FILE, index=False)

    
    
# Configuração do Streamlit
st.sidebar.title("Menu")
pagina = st.sidebar.selectbox("Escolha uma opção",
                               ["Cadastrar Cliente", "Cadastrar Produto", "Registrar Venda", "Clientes", "Relatório de Vendas"])

if pagina == "Cadastrar Cliente":
    st.header("Cadastrar Novo Cliente")
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")

    telefone_formatado = ""
    if telefone_raw:
        if len(telefone_raw) == 11 and telefone_raw.isdigit():
            telefone_formatado = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
            st.sucess(f"Telefone formatado: {telefone_formatado}")
        elif telefone_raw:
            st.warning("Formato de telefone inválido.")

        if st.button("Salvar Cliente"):
            if nome and telefone:
                salvar_cliente(nome, telefone)
                st.success("Cliente cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

        

elif pagina == "Cadastrar Produto":
    st.header("Cadastrar ou Editar Produto")

    produtos = carregar_produtos()

    modo = st.radio("Modo", ["Adicionar Novo", "Editar Existente"])

    if modo == "Adicionar Novo":
        nome_produto = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0, format="%.2f")

        if st.button("Salvar Produto"):
            if nome_produto:
                salvar_produto(nome_produto, preco)
                st.success("Produto cadastrado com sucesso!")
            else:
                st.error("Informe o nome do produto.")

    else:
        if produtos.empty:
            st.info("Nenhum produto cadastrado para editar.")
        else:
            produto_selecionado = st.selectbox("Selecione um produto", produtos['nome'])
            produto_row = produtos[produtos['nome'] == produto_selecionado].iloc[0]
            novo_nome = st.text_input("Nome do Produto", value=produto_row['nome'])
            novo_preco = st.number_input("Preço", min_value=0.0, format="%.2f", value=produto_row['preco'])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Salvar Alterações"):
                    editar_produto(produto_row['id'], novo_nome, novo_preco)
                    st.success("Produto atualizado com sucesso!")

            with col2:
                if st.button("Excluir Produto"):
                    excluir_produto(produto_row['id'])
                    st.warning("Produto excluído com sucesso!")

    # Exibir tabela de produtos
    st.subheader("Produtos Cadastrados")
    produtos_atualizados = carregar_produtos()
    if produtos_atualizados.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.dataframe(produtos_atualizados.rename(columns={"id": "ID", "nome": "Nome", "preco": "Preço (R$)"}))

elif pagina == "Clientes":
    st.header("Clientes Cadastrados")
    clientes = carregar_clientes()
    if clientes.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        st.dataframe(clientes.rename(columns={"id": "ID", "nome": "Nome", "telefone": "Telefone"}))
        st.subheader("Gerenciar Clientes")
        cliente_selecionado = st.selectbox("Selecione um cliente para gerenciar", clientes['nome'])
        if st.button("Excluir Cliente"):
            cliente_row = clientes[clientes['nome'] == cliente_selecionado].iloc[0]
            excluir_cliente(cliente_row['id'])
            st.success("Cliente excluído com sucesso!")

        if st.button("Editar Cliente"):
            cliente_row = clientes[clientes['nome'] == cliente_selecionado].iloc[0]
            novo_nome = st.text_input("Nome do Cliente", value=cliente_row['nome'])
            novo_telefone = st.text_input("Telefone", value=cliente_row['telefone'])
            if st.button("Salvar Alterações"):
                salvar_cliente(novo_nome, novo_telefone)
                st.success("Cliente atualizado com sucesso!")


elif pagina == "Registrar Venda":
    st.header("Registrar Venda")
    clientes = carregar_clientes()
    if clientes.empty:
        st.warning("Nenhum cliente cadastrado. Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Cliente", clientes['nome'])
        cliente_id = clientes.loc[clientes['nome'] == cliente_nome, 'id'].values[0]
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        produto = carregar_produtos()
        if produto.empty:
            st.warning("Nenhum produto cadastrado. Cadastre um produto primeiro.")
        else:
            produto_nome = st.selectbox("Produto", produto['nome'])
            produto_preco = produto.loc[produto['nome'] == produto_nome, 'preco'].values[0]
            st.write(f"Preço: R$ {produto_preco:.2f}")


        if st.button("Registrar Venda"):
            if produto:
                salvar_venda(cliente_id, produto_nome, quantidade)
                st.success("Venda registrada com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos.")

elif pagina == "Relatório de Vendas":
    st.header("Relatório de Consumo Mensal")
    vendas = carregar_vendas()
    clientes = carregar_clientes()
    
    if vendas.empty:
        st.warning("Nenhuma venda registrada.")

    else: 
        vendas['data'] = pd.to_datetime(vendas['data'])
        vendas['mes'] = vendas['data'].dt.to_period('M').astype(str)

        cliente_nome = ['todos'] + clientes['nome'].tolist()
        cliente_selecionado = st.selectbox("Selecione um cliente", cliente_nome)

        data_min = vendas['data'].min()
        data_max = vendas['data'].max()
        data_inicio = st.date_input("Data de Início", data_min)
        data_fim = st.date_input("Data Final", data_max)

    vendas_filtradas = vendas[(vendas['data'] >= pd.to_datetime(data_inicio)) & (vendas['data'] <= pd.to_datetime(data_fim))]

    if cliente_selecionado != 'todos':
        cliente_id = clientes.loc[clientes['nome'] == cliente_selecionado, 'id'].values[0]
        vendas_filtradas = vendas_filtradas[vendas_filtradas['cliente_id'] == cliente_id]

    if vendas_filtradas.empty:
        st.info("Nenhuma venda encontrada para o período selecionado.")

    else:
        
        st.subheader("Consumo Mensal")
        vendas_filtradas['mes'] = vendas_filtradas['data'].dt.to_period('M').astype(str)
        vendas_mes = vendas_filtradas.groupby('mes')['quantidade'].sum()
        st.line_chart(vendas_mes)

        st.subheader("Produtos mais vendidos")
        vendas_produto = vendas_filtradas.groupby('produto')['quantidade'].sum().reset_index()
        st.bar_chart(vendas_produto)
        
                                                    



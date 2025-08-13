import streamlit as st
import pandas as pd
import os 
from datetime import datetime

CLIENTES_FILE = 'clientes.csv'
VENDAS_FILE = 'vendas.csv'
PRODUTOS_FILE = 'produtos.csv'

# Verifica se os arquivos CSV existem, caso não, cria-os com colunas padrão
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
    df = pd.read_csv(CLIENTES_FILE)
    return df

def carregar_vendas():
    if os.path.getsize(VENDAS_FILE) == 0:
        return pd.DataFrame(columns=["cliente_id", "produto", "quantidade", "data"])
    df = pd.read_csv(VENDAS_FILE)
    # Garante tipo numérico para quantidade
    if 'quantidade' in df.columns:
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
    return df

def carregar_produtos():
    if os.path.getsize(PRODUTOS_FILE) == 0:
        return pd.DataFrame(columns=["id", "nome", "preco"])
    df = pd.read_csv(PRODUTOS_FILE)
    # Garante tipo numérico para preço
    if 'preco' in df.columns:
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0.0)
    return df

def salvar_cliente(nome, telefone):
    df = carregar_clientes()
    novo_id = df['id'].max() + 1 if not df.empty else 1
    novo_cliente = pd.DataFrame({'id': [int(novo_id)], 'nome': [nome], 'telefone': [telefone]})
    df = pd.concat([df, novo_cliente], ignore_index=True)
    df.to_csv(CLIENTES_FILE, index=False)

def salvar_venda(cliente_id, produto, quantidade):
    df = carregar_vendas()
    nova_venda = pd.DataFrame([[int(cliente_id), produto, int(quantidade), datetime.today().strftime('%Y-%m-%d')]],
                               columns=['cliente_id', 'produto', 'quantidade', 'data'])
    df = pd.concat([df, nova_venda], ignore_index=True)
    df.to_csv(VENDAS_FILE, index=False)

def salvar_produto(nome, preco):
    df = carregar_produtos()
    novo_id = df['id'].max() + 1 if not df.empty else 1
    novo_produto = pd.DataFrame({'id': [int(novo_id)], 'nome': [nome], 'preco': [float(preco)]})
    df = pd.concat([df, novo_produto], ignore_index=True)
    df.to_csv(PRODUTOS_FILE, index=False)
    
def excluir_produto(produto_id):
    df = carregar_produtos()
    df = df[df['id'] != int(produto_id)]
    df.to_csv(PRODUTOS_FILE, index=False)

def editar_produto(produto_id, novo_nome, novo_preco):
    df = carregar_produtos()
    df.loc[df['id'] == int(produto_id), ['nome', 'preco']] = [novo_nome, float(novo_preco)]
    df.to_csv(PRODUTOS_FILE, index=False)

def listar_clientes():
    df = carregar_clientes()
    if df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        st.dataframe(df.rename(columns={"id": "ID", "nome": "Nome", "telefone": "Telefone"}))

def excluir_cliente(cliente_id):
    df = carregar_clientes()
    df = df[df['id'] != int(cliente_id)]
    df.to_csv(CLIENTES_FILE, index=False)

def editar_cliente(cliente_id, novo_nome, novo_telefone):
    df = carregar_clientes()
    df.loc[df['id'] == int(cliente_id), ['nome', 'telefone']] = [novo_nome, novo_telefone]
    df.to_csv(CLIENTES_FILE, index=False)
      
# Configuração de UI
st.sidebar.title("Menu")
pagina = st.sidebar.selectbox("Escolha uma opção",
                               ["Cadastrar Cliente", "Cadastrar Produto", "Registrar Venda", "Clientes", "Relatório de Vendas"])

if pagina == "Cadastrar Cliente":
    st.header("Cadastrar Novo Cliente")
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone (apenas números, com DDD)")

    if st.button("Salvar Cliente"):
        if nome and telefone:
            if len(telefone) == 11 and telefone.isdigit():
                telefone_formatado = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
                salvar_cliente(nome, telefone_formatado)
                st.success("Cliente cadastrado com sucesso!")
            else:
                st.warning("Formato de telefone inválido. Salvo sem formatação.")
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
            novo_preco = st.number_input("Preço", min_value=0.0, format="%.2f", value=float(produto_row['preco']))

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
                editar_cliente(cliente_row['id'], novo_nome, novo_telefone)
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
            st.write(f"Preço: R$ {float(produto_preco):.2f}")

        if st.button("Registrar Venda"):
            if not produto.empty:
                salvar_venda(cliente_id, produto_nome, quantidade)
                st.success("Venda registrada com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos.")

# --- Relatório de Vendas ---
elif pagina == "Relatório de Vendas":
    st.header("Relatório de Consumo Mensal")
    vendas = carregar_vendas()
    clientes = carregar_clientes()
    produtos = carregar_produtos()
    
    if vendas.empty:
        st.warning("Nenhuma venda registrada.")

    else:
        vendas['data'] = pd.to_datetime(vendas['data'], errors='coerce')
        vendas = vendas.dropna(subset=['data'])

        cliente_opcoes = ['todos'] + clientes['nome'].tolist()
        cliente_selecionado = st.selectbox("Selecione um cliente", cliente_opcoes)

        data_min = vendas['data'].min().date()
        data_max = vendas['data'].max().date()
        data_inicio = st.date_input('Data de início', data_min)
        data_fim = st.date_input('Data final', data_max)

        vendas_filtradas = vendas[(vendas['data'].dt.date >= data_inicio) & (vendas['data'].dt.date <= data_fim)]

        if cliente_selecionado != 'todos' and not clientes.empty:
            cliente_id = int(clientes.loc[clientes['nome'] == cliente_selecionado, 'id'].values[0])
            vendas_filtradas = vendas_filtradas[vendas_filtradas['cliente_id'] == cliente_id]

        if vendas_filtradas.empty:
            st.warning("Nenhuma venda encontrada para o período selecionado.")
        else:
            vendas_filtradas['mes'] = vendas_filtradas['data'].dt.to_period('M').astype(str)

            st.subheader('Consumo Mensal')
            vendas_mes = vendas_filtradas.groupby('mes')['quantidade'].sum().reset_index()
            st.line_chart(vendas_mes.set_index('mes'))

            st.subheader('Produtos mais vendidos')
            vendas_produto = vendas_filtradas.groupby('produto')['quantidade'].sum().reset_index()
            st.bar_chart(vendas_produto.set_index('produto'))

            st.subheader('Faturamento no período')
            if not produtos.empty:
                vendas_valor = vendas_filtradas.merge(
                    produtos[['nome', 'preco']],
                    left_on='produto', right_on='nome', how='left'
                )
                vendas_valor['preco'] = pd.to_numeric(vendas_valor['preco'], errors='coerce').fillna(0.0)
                vendas_valor['valor_total'] = vendas_valor['quantidade'] * vendas_valor['preco']

                total_periodo = vendas_valor['valor_total'].sum()
                # Formato brasileiro simples
                st.metric('Total R$', f'{total_periodo:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))

                st.dataframe(
                    vendas_valor[['data', 'produto', 'quantidade', 'preco', 'valor_total']]
                    .rename(columns={'preco': 'Preço (R$)', 'valor_total': 'Valor Total (R$)'}),
                    use_container_width=True
                )
            else:
                st.info('Cadastre produtos com preço para ver o faturamento.')

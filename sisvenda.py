import sqlite3
import os

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def inicializar_db():
    conn = sqlite3.connect('sistema_gestao.db')
    cursor = conn.cursor()
    
    # Tabela de Usuários (Login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id),
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- FUNÇÕES DE OPERAÇÃO ---

def cadastrar_usuario():
    print("\n--- Cadastro de Novo Usuário ---")
    user = input("Usuário: ")
    senha = input("Senha: ")
    try:
        conn = sqlite3.connect('sistema_gestao.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?, ?)", (user, senha))
        conn.commit()
        print("Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: Este nome de usuário já existe.")
    finally:
        conn.close()

def login():
    print("\n--- Login ---")
    user = input("Usuário: ")
    senha = input("Senha: ")
    
    conn = sqlite3.connect('sistema_gestao.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND senha = ?", (user, senha))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def cadastrar_cliente():
    nome = input("Nome do Cliente: ")
    email = input("Email: ")
    conn = sqlite3.connect('sistema_gestao.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, email) VALUES (?, ?)", (nome, email))
    conn.commit()
    conn.close()
    print("Cliente cadastrado!")

def cadastrar_produto():
    nome = input("Nome do Produto: ")
    preco = float(input("Preço: "))
    conn = sqlite3.connect('sistema_gestao.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
    conn.commit()
    conn.close()
    print("Produto cadastrado!")

def registrar_venda():
    conn = sqlite3.connect('sistema_gestao.db')
    cursor = conn.cursor()
    
    # Lista clientes e produtos para facilitar a escolha
    print("\nClientes disponíveis:")
    for row in cursor.execute("SELECT id, nome FROM clientes"): print(row)
    c_id = int(input("ID do Cliente: "))
    
    print("\nProdutos disponíveis:")
    for row in cursor.execute("SELECT id, nome, preco FROM produtos"): print(row)
    p_id = int(input("ID do Produto: "))
    
    qtd = int(input("Quantidade: "))
    
    cursor.execute("INSERT INTO vendas (cliente_id, produto_id, quantidade) VALUES (?, ?, ?)", (c_id, p_id, qtd))
    conn.commit()
    conn.close()
    print("Venda registrada com sucesso!")

# --- MENU PRINCIPAL ---

def menu_sistema():
    while True:
        print("\n=== SISTEMA DE GESTÃO ===")
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Produto")
        print("3. Registrar Venda")
        print("4. Sair")
        opcao = input("Escolha: ")
        
        if opcao == '1': cadastrar_cliente()
        elif opcao == '2': cadastrar_produto()
        elif opcao == '3': registrar_venda()
        elif opcao == '4': break
        else: print("Opção inválida.")

def main():
    inicializar_db()
    
    while True:
        print("\n--- BEM VINDO ---")
        print("1. Login")
        print("2. Criar Conta")
        print("3. Sair")
        escolha = input("Opção: ")
        
        if escolha == '1':
            usuario_logado = login()
            if usuario_logado:
                print(f"\nBem-vindo, {usuario_logado[1]}!")
                menu_sistema()
            else:
                print("Usuário ou senha incorretos.")
        elif escolha == '2':
            cadastrar_usuario()
        elif escolha == '3':
            break

if __name__ == "__main__":
    main()

import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def inicializar_db():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    
    # Tabela de Administradores (Acesso ao sistema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            id_produto INTEGER,
            quantidade INTEGER,
            total REAL,
            data TEXT,
            FOREIGN KEY(id_cliente) REFERENCES clientes(id),
            FOREIGN KEY(id_produto) REFERENCES produtos(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- FUNÇÕES DE AUTENTICAÇÃO ---

def cadastrar_admin():
    print("\n--- NOVO ADMINISTRADOR ---")
    user = input("Usuário: ")
    senha = input("Senha: ")
    try:
        conn = sqlite3.connect('sistema_vendas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admins (usuario, senha) VALUES (?, ?)", (user, senha))
        conn.commit()
        print(f"✅ Admin '{user}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("❌ Erro: Este nome de usuário já existe.")
    finally:
        conn.close()

def login():
    print("\n--- LOGIN DO SISTEMA ---")
    user = input("Usuário: ")
    senha = input("Senha: ")
    
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE usuario = ? AND senha = ?", (user, senha))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

# --- FUNÇÕES DE CADASTRO ---

def menu_cadastros():
    while True:
        print("\n--- PAINEL DE GESTÃO ---")
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Produto")
        print("3. Registrar Venda")
        print("4. Relatório de Vendas")
        print("5. Sair (Logout)")
        
        opcao = input("Escolha: ")
        
        if opcao == '1':
            nome = input("Nome: ")
            email = input("Email: ")
            executar_query("INSERT INTO clientes (nome, email) VALUES (?, ?)", (nome, email))
            print("✅ Cliente salvo!")
            
        elif opcao == '2':
            nome = input("Produto: ")
            preco = float(input("Preço: "))
            estoque = int(input("Qtd em Estoque: "))
            executar_query("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
            print("✅ Produto salvo!")
            
        elif opcao == '3':
            realizar_venda()
            
        elif opcao == '4':
            exibir_vendas()
            
        elif opcao == '5':
            break

# --- LÓGICA DE VENDAS ---

def realizar_venda():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    
    # Listar Clientes e Produtos para escolha
    print("\n--- SELECIONE O CLIENTE ---")
    clientes = cursor.execute("SELECT id, nome FROM clientes").fetchall()
    for c in clientes: print(f"[{c[0]}] {c[1]}")
    id_c = int(input("ID do Cliente: "))
    
    print("\n--- SELECIONE O PRODUTO ---")
    produtos = cursor.execute("SELECT id, nome, preco FROM produtos").fetchall()
    for p in produtos: print(f"[{p[0]}] {p[1]} - R$ {p[2]}")
    id_p = int(input("ID do Produto: "))
    
    qtd = int(input("Quantidade: "))
    
    # Busca preço e calcula total
    cursor.execute("SELECT preco FROM produtos WHERE id = ?", (id_p,))
    preco_unitario = cursor.fetchone()[0]
    total = preco_unitario * qtd
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    cursor.execute("INSERT INTO vendas (id_cliente, id_produto, quantidade, total, data) VALUES (?, ?, ?, ?, ?)",
                   (id_c, id_p, qtd, total, data_hoje))
    
    # Baixa no estoque
    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, id_p))
    
    conn.commit()
    conn.close()
    print(f"✅ Venda finalizada! Total: R$ {total:.2f}")

def exibir_vendas():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    query = '''
        SELECT v.id, c.nome, p.nome, v.quantidade, v.total, v.data 
        FROM vendas v
        JOIN clientes c ON v.id_cliente = c.id
        JOIN produtos p ON v.id_produto = p.id
    '''
    print("\n--- HISTÓRICO DE VENDAS ---")
    for linha in cursor.execute(query):
        print(f"Venda {linha[0]} | Cliente: {linha[1]} | Item: {linha[2]} | Qtd: {linha[3]} | Total: R${linha[4]} | Data: {linha[5]}")
    conn.close()

def executar_query(sql, params=()):
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

# --- INTERFACE PRINCIPAL ---

def main():
    inicializar_db()
    while True:
        print("\n=== SISTEMA ERP v1.0 ===")
        print("1. Login Admin")
        print("2. Cadastrar Novo Admin")
        print("3. Encerrar")
        
        escolha = input("Opção: ")
        
        if escolha == '1':
            adm = login()
            if adm:
                print(f"\n🔓 Acesso autorizado! Bem-vindo, {adm[1]}.")
                menu_cadastros()
            else:
                print("\n❌ Usuário ou senha incorretos.")
        elif escolha == '2':
            cadastrar_admin()
        elif escolha == '3':
            print("Saindo...")
            break

if __name__ == "__main__":
    main()

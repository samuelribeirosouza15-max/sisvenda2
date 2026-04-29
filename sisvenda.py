import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_muito_segura_123'

# Configuração do caminho do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(basedir, 'sisvenda.db')

# --- FUNÇÕES DE BANCO DE DADOS ---

def get_db_connection():
    """Cria uma conexão com o banco e permite acessar colunas pelo nome."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Isso permite usar cliente['nome'] em vez de cliente[1]
    return conn

def init_db():
    """Cria as tabelas e o usuário admin inicial se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Criar tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Criar tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0
        )
    ''')
    
    # Criar tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            total REAL DEFAULT 0.0,
            FOREIGN KEY (cliente_id) REFERENCES cliente (id)
        )
    ''')
    
    # Criar usuário admin padrão
    admin_exists = cursor.execute('SELECT * FROM usuario WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        hashed_pw = generate_password_hash('1234')
        cursor.execute('INSERT INTO usuario (username, password) VALUES (?, ?)', ('admin', hashed_pw))
    
    conn.commit()
    conn.close()

# Inicializa o banco ao rodar o app
init_db()

# --- AUXILIAR DE LOGIN ---
def login_obrigatorio():
    return 'user_id' in session

# --- ROTAS ---

@app.route('/')
def index():
    if not login_obrigatorio(): return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuario WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash('Usuário ou senha incorretos!', 'danger')
    return render_template('login.html')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        conn.execute('INSERT INTO cliente (nome, email) VALUES (?, ?)', (nome, email))
        conn.commit()
        flash('Cliente cadastrado!', 'success')
        
    lista = conn.execute('SELECT * FROM cliente').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista)

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            preco = float(request.form['preco'])
            estoque = int(request.form['estoque'])
            conn.execute('INSERT INTO produto (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
            conn.commit()
            flash('Produto cadastrado!', 'success')
        except ValueError:
            flash('Erro nos dados. Use ponto para decimais.', 'warning')
        
    lista = conn.execute('SELECT * FROM produto').fetchall()
    conn.close()
    return render_template('produtos.html', produtos=lista)

@app.route('/venda', methods=['GET', 'POST'])
def nova_venda():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        total = float(request.form['total'])
        conn.execute('INSERT INTO venda (cliente_id, total) VALUES (?, ?)', (cliente_id, total))
        conn.commit()
        flash('Venda registrada!', 'success')
    
    clientes = conn.execute('SELECT * FROM cliente').fetchall()
    produtos = conn.execute('SELECT * FROM produto').fetchall()
    conn.close()
    
    return render_template('vendas.html', clientes=clientes, produtos=produtos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

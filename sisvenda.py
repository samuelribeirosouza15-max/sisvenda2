from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_vendas'
# Define o caminho do banco de dados para evitar erros de permissão
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sisvenda.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    total = db.Column(db.Float, default=0.0)

# Criar o banco de dados e usuário inicial
with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username='admin').first():
        # Gerar senha hash (deixando o método automático para evitar erros de versão)
        hashed_pw = generate_password_hash('1234')
        admin = Usuario(username='admin', password=hashed_pw)
        db.session.add(admin)
        db.session.commit()

# --- ROTAS ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        
        flash('Usuário ou senha inválidos!')
    return render_template('login.html')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        novo_cliente = Cliente(nome=request.form['nome'], email=request.form['email'])
        db.session.add(novo_cliente)
        db.session.commit()
        flash('Cliente cadastrado!')
        
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        novo_prod = Produto(
            nome=request.form['nome'], 
            preco=float(request.form['preco']), 
            estoque=int(request.form['estoque'])
        )
        db.session.add(novo_prod)
        db.session.commit()
        flash('Produto cadastrado!')
        
    lista = Produto.query.all()
    return render_template('produtos.html', produtos=lista)

@app.route('/venda', methods=['GET', 'POST'])
def nova_venda():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    
    if request.method == 'POST':
        venda = Venda(cliente_id=request.form['cliente_id'], total=float(request.form['total']))
        db.session.add(venda)
        db.session.commit()
        flash('Venda registrada com sucesso!')
        
    return render_template('vendas.html', clientes=clientes, produtos=produtos)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

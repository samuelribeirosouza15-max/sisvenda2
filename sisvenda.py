import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_muito_segura_123'

# Configuração do caminho do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sisvenda.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
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

# Inicialização do Banco
with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username='admin').first():
        admin = Usuario(username='admin', password=generate_password_hash('1234'))
        db.session.add(admin)
        db.session.commit()

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
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Usuário ou senha incorretos!', 'danger')
    return render_template('login.html')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    if request.method == 'POST':
        novo = Cliente(nome=request.form['nome'], email=request.form['email'])
        db.session.add(novo)
        db.session.commit()
        flash('Cliente cadastrado!', 'success')
        
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            novo = Produto(
                nome=request.form['nome'], 
                preco=float(request.form['preco']), 
                estoque=int(request.form['estoque'])
            )
            db.session.add(novo)
            db.session.commit()
            flash('Produto cadastrado!', 'success')
        except ValueError:
            flash('Erro nos dados. Use ponto para decimais e números inteiros no estoque.', 'warning')
        
    lista = Produto.query.all()
    return render_template('produtos.html', produtos=lista)

@app.route('/venda', methods=['GET', 'POST'])
def nova_venda():
    if not login_obrigatorio(): return redirect(url_for('login'))
    
    if request.method == 'POST':
        venda = Venda(cliente_id=request.form['cliente_id'], total=float(request.form['total']))
        db.session.add(venda)
        db.session.commit()
        flash('Venda registrada!', 'success')
        
    return render_template('vendas.html', clientes=Cliente.query.all(), produtos=Produto.query.all())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, render_template, abort, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/banco.db'

db = SQLAlchemy(app)


# banco de Instituiçãos
class Instituicao(db.Model):
    __tablename__ = 'instituicao'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(250), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    end = db.Column(db.String(250), nullable=False)
    # determinando relacionamento
    ordens = db.relationship('Ordem', backref="instituicao", cascade="all,delete-orphan", lazy='dynamic')

    def __init__(self, nome, telefone, end):
        self.nome = nome
        self.telefone = telefone
        self.end = end


# Função
class Funcao(db.Model):
    __tablename__ = 'funcao'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(250), nullable=False)
    ordens = db.relationship('Ordem', backref="funcao", cascade="all,delete-orphan", lazy='dynamic')

    def __init__(self, descricao):
        self.descricao = descricao


# Equipamento
class Equipamento(db.Model):
    __tablename__ = "equipamento"

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(250), nullable=False)
    ordens = db.relationship('Ordem', backref="equipamento", cascade="all,delete-orphan", lazy='dynamic')

    def __init__(self, descricao):
        self.descricao = descricao


# Categoria
class Categoria(db.Model):
    __tablename__ = "categoria"

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(250), nullable=False)
    ordens = db.relationship('Ordem', backref="categoria", cascade="all,delete-orphan", lazy='dynamic')

    def __init__(self, descricao):
        self.descricao = descricao


# Ordem Serviço
class Ordem(db.Model):
    __tablename__ = "ordem"

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(250), nullable=False)
    data = db.Column(db.DateTime)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao._id'))
    funcao_id = db.Column(db.Integer, db.ForeignKey('funcao._id'))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria._id'))
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamento._id'))

    def __init__(self, descricao, instituicao_id, funcao_id, categoria_id, equipamento_id):
        self.descricao = descricao
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.instituicao_id = instituicao_id
        self.funcao_id = funcao_id
        self.categoria_id = categoria_id
        self.equipamento_id = equipamento_id


# banco de usuarios
class User(db.Model):
    __tablename__ = 'user'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    login = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __init__(self, name, login, password):
        self.name = name
        self.login = login
        self.password = password

    # funções do flask-login
    def is_authenticated(self):
        return True

    def is_active():
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self._id)

    def __repr__(self):
        return '<User %r>' % (self.name)


# banco de posts
class Post(db.Model):
    __tablename__ = 'post'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.DateTime)
    titulo = db.Column(db.String(80))
    descricao = db.Column(db.String(300))

    def __init__(self, titulo, descricao):
        self.data = datetime.utcnow()
        self.titulo = titulo
        self.descricao = descricao


# comitando no banco
db.create_all()

# criando usuario admin
user = User("admin", "admin", "admin")
db.session.add(user)
db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'Login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template("home.html", posts=Post.query.order_by(Post.data.desc()).all())


# criar novo post
@app.route('/Post/Create', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        post = Post(request.form["titulo"], request.form['descricao'])
        db.session.add(post)
        db.session.commit()
    return render_template('newpost.html')


# atualizar post
@app.route('/Post/Update/<int:post_id>', methods=['GET', 'POST'])
def updatePost(post_id):
    post_item = Post.query.get(post_id)
    if request.method == 'GET':
        return render_template('postupdate.html', post=post_item)
    post_item.titulo = request.form['titulo']
    post_item.descricao = request.form['descricao']
    post_item.done = ('done.%d' % post_id) in request.form
    db.session.commit()
    return redirect(url_for('home'))


# deletar post
@app.route('/Post/Delete/<int:post_id>', methods=['GET', 'POST'])
def deletePost(post_id):
    post_item = Post.query.get(post_id)
    db.session.delete(post_item)
    db.session.commit()
    return redirect(url_for('home'))


# criar admin
@app.route('/Admin/Create', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        user = User(request.form['name'], request.form['login'], request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new.html')


# listar admin
@app.route('/Admin/')
@login_required
def admin():
    return render_template('admin.html',
                           users=User.query.all()
                           )


# update admin
@app.route('/Admin/Delete/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def deleteAdmin(admin_id):
    admin_item = User.query.get(admin_id)
    db.session.delete(admin_item)
    db.session.commit()
    return redirect(url_for('admin'))


# update admin
@app.route('/Admin/Update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def updateAdmin(user_id):
    user_item = User.query.get(user_id)
    if request.method == 'GET':
        return render_template('admupdate.html', user=user_item)
    user_item.name = request.form['name']
    user_item.login = request.form['login']
    user_item.password = request.form['password']
    user_item.done = ('done.%d' % user_id) in request.form
    db.session.commit()
    return redirect(url_for('admin'))


# criar instituição
@app.route('/Instituicao/Create', methods=['GET', 'POST'])
def createInstituicao():
    if request.method == 'GET':
        return render_template('instituicaoCreate.html')
    inst_item = Instituicao(request.form['nome'], request.form['telefone'], request.form['endereco'])
    db.session.add(inst_item)
    db.session.commit()
    return redirect(url_for('instituicao'))


# update instituição
@app.route('/Instituicao/Update/<int:inst_id>', methods=['GET', 'POST'])
def updateInstituicao(inst_id):
    inst_item = Instituicao.query.get(inst_id)
    if request.method == 'GET':
        return render_template('instituicaoUpdate.html', inst=inst_item)
    inst_item.nome = request.form['nome']
    inst_item.telefone = request.form['telefone']
    inst_item.end = request.form['end']
    inst_item.done = ('done.%d' % inst_id) in request.form
    db.session.commit()
    return redirect(url_for('instituicao'))


# deletar instituição
@app.route('/Instituicao/Delete/<int:inst_id>', methods=['GET', 'POST'])
def deleteInstituicao(inst_id):
    inst_item = Instituicao.query.get(inst_id)
    db.session.delete(inst_item)
    db.session.commit()
    return redirect(url_for('instituicao'))


# Instituição Listar
@app.route('/Instituicao/')
@login_required
def instituicao():
    return render_template('instituicao.html',
                           insts=Instituicao.query.all())


# criar Função
@app.route('/Funcao/Create', methods=['GET', 'POST'])
def createfuncao():
    if request.method == 'GET':
        return render_template('funcaoCreate.html')
    func_item = Funcao(request.form['desc'])
    db.session.add(func_item)
    db.session.commit()
    return redirect(url_for('funcao'))


# update função
@app.route('/Funcao/Update/<int:func_id>', methods=['GET', 'POST'])
def updatefuncao(func_id):
    func_item = Funcao.query.get(func_id)
    if request.method == 'GET':
        return render_template('funcaoUpdate.html', func=func_item)
    func_item.nome = request.form['desc']
    func_item.done = ('done.%d' % func_id) in request.form
    db.session.commit()
    return redirect(url_for('funcao'))


# deletar função
@app.route('/Funcao/Delete/<int:func_id>', methods=['GET', 'POST'])
def deletefuncao(func_id):
    func_item = Funcao.query.get(func_id)
    db.session.delete(func_item)
    db.session.commit()
    return redirect(url_for('funcao'))


# listar Função
@app.route('/Funcao/')
@login_required
def funcao():
    return render_template('Funcao.html',
                           funcs=Funcao.query.all())


# criar Equipamento
@app.route('/Equipamento/Create', methods=['GET', 'POST'])
def createequipamento():
    if request.method == 'GET':
        return render_template('equipamentoCreate.html')
    equip_item = Equipamento(request.form['desc'])
    db.session.add(equip_item)
    db.session.commit()
    return redirect(url_for('equipamento'))


# update Equipamento
@app.route('/Equipamento/Update/<int:equip_id>', methods=['GET', 'POST'])
def updateequipamento(equip_id):
    equip_item = Equipamento.query.get(equip_id)
    if request.method == 'GET':
        return render_template('equipamentoUpdate.html', equip=equip_item)
    equip_item.nome = request.form['desc']
    equip_item.done = ('done.%d' % equip_id) in request.form
    db.session.commit()
    return redirect(url_for('equipamento'))


# deletar Equipamento
@app.route('/Equipamento/Delete/<int:equip_id>', methods=['GET', 'POST'])
def deleteequipamento(equip_id):
    equip_item = Equipamento.query.get(equip_id)
    db.session.delete(equip_item)
    db.session.commit()
    return redirect(url_for('equipamento'))


# listar Equipamento
@app.route('/Equipamento/')
@login_required
def equipamento():
    return render_template('Equipamento.html',
                           funcs=Equipamento.query.all())


# logar
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')
    login = request.form['login']
    password = request.form['password']
    registered_user = User.query.filter_by(login=login, password=password).first()
    if registered_user is None:
        flash('Usuario ou senha invalido', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Login Realizado')
    return redirect(request.args.get('next') or url_for('home'))


# deslogar
@app.route('/Logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run()

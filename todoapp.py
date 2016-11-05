from datetime import datetime
from flask import Flask, request, flash, url_for,redirect,render_template,abort,g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager,login_user, logout_user, current_user, login_required


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/banco.db'

db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'user'

	_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
	name = db.Column(db.String(250),nullable=False)
	login = db.Column(db.String(250),nullable=False)
	password = db.Column(db.String(250),nullable=False)

	def __init__(self,name,login,password):
		self.name = name
		self.login = login
		self.password = password

	def is_authenticated(self):
		return True

	def  is_active():
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self._id)

	def __repr__(self):
		return '<User %r>' % (self.name)

class Post(db.Model):
	__tablename__ = 'post'

	_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
	data = db.Column(db.DateTime)
	titulo = db.Column(db.String(80))
	descricao = db.Column(db.String(300))

	def __init__(self,titulo,descricao):
		self.data = datetime.utcnow()
		self.titulo = titulo
		self.descricao = descricao


db.create_all()

user = User("admin","admin","admin")
db.session.add(user)
db.session.commit()


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
	return "hello"

@app.route('/home')
def home():
	return render_template("home.html",posts = Post.query.all())

@app.route('/newpost', methods =['GET','POST'])
def newpost():
	if request.method == 'POST':
		post = Post(request.form["titulo"],request.form['descricao'])
		db.session.add(post)
		db.session.commit()
	return render_template('newpost.html')

@app.route('/newpost/<int:post_id>',methods=['GET','POST'])
def updatePost(post_id):
	post_item = Post.query.get(post_id)
	if request.method == 'GET':
		return render_template('postupdate.html',post = post_item)
	post_item.titulo = request.form['titulo']
	post_item.descricao = request.form['descricao']
	post_item.done = ('done.%d' % post_id) in request.form
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/newpost/delete/<int:post_id>',methods=['GET','POST'])
def deletePost(post_id):
	post_item = Post.query.get(post_id)
	db.session.delete(post_item)
	db.session.commit()
	return redirect(url_for('home'))


@app.route('/new',methods=['GET','POST'])
@login_required
def new():
	if request.method == 'POST':
		user = User(request.form['name'],request.form['login'],request.form['password'])
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('index'))
	return render_template('new.html')


@app.route('/admin/')
def admin():

	return render_template('admin.html',
			users = User.query.all()
		)

@app.route('/admin/<int:user_id>', methods = ['GET','POST'])
@login_required
def updateAdmin(user_id):
	user_item = User.query.get(user_id)
	if request.method == 'GET':
		return render_template('admupdate.html',user = user_item)
	user_item.name = request.form['name']
	user_item.login = request.form['login']
	user_item.password = request.form['password']
	user_item.done = ('done.%d' % user_id) in request.form
	db.session.commit()
	return redirect(url_for('admin'))

@app.route('/login',methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))	
	if request.method == 'GET':
		return render_template('login.html')
	login = request.form['login']
	password = request.form['password']
	registered_user = User.query.filter_by(login = login,password = password).first()
	if registered_user is None:
		flash('Usuario ou senha invalido', 'error')
		return redirect(url_for('login'))
	login_user(registered_user)
	flash('Login Realizado')
	return redirect(request.args.get('next') or url_for('index'))
	
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.before_request
def before_request():
	g.user = current_user

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run()


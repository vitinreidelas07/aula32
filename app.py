from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd


app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_secreta"  # Substitua por uma chave secreta segura
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///livros.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    editora = db.Column(db.String(200), default="Sem Editora")
    ativo = db.Column(db.Boolean, default=False)

    def __init__(self, titulo, autor, categoria, ano, editora="Sem Editora", ativo=False):
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.ano = ano
        self.editora = editora
        self.ativo = ativo

    def __repr__(self):
        return f"<Livro {self.titulo}>"
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    


with app.app_context():
    db.create_all()

    # Ler o arquivo CSV para um DataFrame
    df = pd.read_csv("tabela_livros.csv")

    # Adicionar cada livro à base de dados, se ainda não estiverem presentes
    for index, row in df.iterrows():
        if not Livro.query.filter_by(titulo=row["Titulo do Livro"]).first():
            livro = Livro(
                titulo=row["Titulo do Livro"],
                autor=row["Autor"],
                categoria=row["Categoria"],
                ano=row["Ano de Publicação"],
                ativo=row["Ativo"] == "TRUE",
            )
            db.session.add(livro)
    db.session.commit() 
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("inicio"))
        else:
            flash("Login ou senha incorretos. Tente novamente.")
    return render_template("login.html")

@app.route("/inicio")
@login_required
def inicio():
    livros = Livro.query.all()
    return render_template("lista.html", lista_de_livros=livros)

@app.route("/novo")
@login_required
def novo():
    return render_template("novo.html", titulo="Novo Livro")

@app.route("/criar", methods=["POST"])
@login_required
def criar():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    categoria = request.form["categoria"]
    ano = request.form["ano"]
    editora = request.form["editora"]
    livro = Livro(titulo=titulo, autor=autor, categoria=categoria, ano=ano, editora=editora)
    db.session.add(livro)
    db.session.commit()
    return redirect(url_for("inicio"))

@app.route("/editar/<int:id>")
@login_required
def editar(id):
    livro = Livro.query.get(id)
    if livro:
        return render_template("editar.html", livro=livro)
    return redirect(url_for("inicio"))

@app.route("/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar(id):
    livro = Livro.query.get(id)
    if livro:
        livro.titulo = request.form["titulo"]
        livro.autor = request.form["autor"]
        livro.categoria = request.form["categoria"]
        livro.ano = request.form["ano"]
        livro.editora = request.form["editora"]
        db.session.commit()
    return redirect(url_for("inicio"))

@app.route("/deletar/<int:id>")
@login_required
def deletar(id):
    livro = Livro.query.get(id)
    if livro:
        db.session.delete(livro)
        db.session.commit()
    return redirect(url_for("inicio"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

app.run(debug=True)
from tkinter import Message
from flask import Blueprint, request, render_template, redirect, session, flash, url_for,jsonify
from modelos import Moderador
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from extensoes import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

s = URLSafeTimedSerializer('chave_secreta_para_token')

principal_blueprint = Blueprint(
    "principal", __name__, template_folder="../vistas/templates")


@principal_blueprint.route("/", methods=["GET", "POST"])
def index():
    if session.get("usuario"):
        flash("Você já está logado.", "warning")
        return redirect("/painel")

    if request.method == "GET":
        return render_template("login.html")

    senha = request.form["senha"]
    email = request.form["email"]

    moderador = Moderador.query.filter_by(email=email).first()
    if moderador is None:
        flash("Email ou senha incorretos.", "danger")
        return redirect("/")

    if not check_password_hash(moderador.senha_hash, senha):
        flash("Email ou senha incorretos.", "danger")
        return redirect("/")

    session["usuario"] = moderador.id
    flash("Logado com sucesso!", "success")
    return redirect("/painel")


@principal_blueprint.route("/esqueci_a_senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "GET":
        return render_template("esqueci_a_senha.html")
    email = request.form["email"]
    if not Moderador.query.filter_by(email=email).first():
        flash("Email não cadastrado.", "danger")
        return redirect("/esqueci_a_senha")
    token = s.dumps(email, salt='recuperacao-senha')
    link = url_for(
        "principal.mudar_senha",
        token=token,
        _external=True,  # Gera url completa pensando no render, sem a necessidade do localhost
    )
    msg = Message(
        subject="Recuperação de senha",
        recipients=[email],
        body=f"Clique no link para redefinir sua senha:\n\n{link}",
    )
    mail.send(msg)
    flash("Email de recuperação enviado!", "info")
    return redirect("/")


@principal_blueprint.route('/mudar_senha/<token>', methods=['GET', 'POST'])
def mudar_senha(token):
    email = validar_token(token)
    if email == "expirado":
        flash("O link de recuperação expirou. Solicite um novo link.", "warning")
        return redirect("/esqueci_a_senha")
    if email is None:
        flash("Link de recuperação inválido.", "danger")
        return redirect("/recuperacao_senha")
    if request.method == 'GET':
        return render_template('mudar_senha.html', token=token)
    nova_senha = request.form['senha']
    nova_senha_confirmar = request.form['senha_confirmar']
    if nova_senha != nova_senha_confirmar:
        flash("As senhas não coincidem.", "danger")
        return redirect(f'/mudar_senha/{token}')
    novo_hash = generate_password_hash(nova_senha)
    moderador = Moderador.query.filter_by(email=email).first()
    moderador.senha_hash = novo_hash
    moderador.salvar()
    flash("Senha alterada com sucesso!", "success")
    return redirect('/')


def validar_token(token, expiracao=3600):
    try:
        email = s.loads(token, salt='recuperacao-senha', max_age=expiracao)
        return email
    except SignatureExpired:
        return "expirado"
    except BadSignature:
        return None



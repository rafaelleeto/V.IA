from flask import Blueprint, request, render_template, redirect, session, flash, url_for,jsonify
from modelos import Moderador
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from extensoes import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


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
    if moderador is None or moderador.ativo == False:
        flash("Email ou senha incorretos.", "danger")
        return redirect("/")

    if not check_password_hash(moderador.senha_hash, senha):
        flash("Email ou senha incorretos.", "danger")
        return redirect("/")

    session["usuario"] = moderador.id
    flash("Logado com sucesso!", "success")
    return redirect("/painel")


def get_serializer():
    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY não configurada!")
    return URLSafeTimedSerializer(secret_key)

# Função para validar token
def validar_token(token, expiracao=3600):
    s = get_serializer()
    try:
        email = s.loads(token, salt="recuperacao-senha", max_age=expiracao)
        return email
    except SignatureExpired:
        return "expirado"
    except BadSignature:
        return None

@principal_blueprint.route("/esqueci_a_senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "GET":
        return render_template("esqueci_a_senha.html")

    email = request.form.get("email")
    if not email:
        flash("Informe um email válido.", "danger")
        return redirect("/esqueci_a_senha")

    moderador = Moderador.query.filter_by(email=email).first()
    if not moderador:
        flash("Email não cadastrado.", "danger")
        return redirect("/esqueci_a_senha")

    # Cria token
    s = get_serializer()
    token = s.dumps(email, salt="recuperacao-senha")

    # Gera link de mudança de senha
    link = url_for(
        "principal.mudar_senha",
        token=token,
        _external=True  # O Flask vai usar http/https correto no Render
    )

    # Envia email (verifique configuração no Render)
    try:
        msg = Message(
            subject="Recuperação de senha",
            recipients=[email],
            body=f"Clique no link para redefinir sua senha:\n\n{link}"
        )
        mail.send(msg)
        flash("Email de recuperação enviado!", "info")
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar email: {e}")
        flash("Erro ao enviar email. Tente novamente mais tarde.", "danger")

    return redirect("/")

@principal_blueprint.route("/mudar_senha/<token>", methods=["GET", "POST"])
def mudar_senha(token):
    email = validar_token(token)
    if email == "expirado":
        flash("O link de recuperação expirou. Solicite um novo link.", "warning")
        return redirect("/esqueci_a_senha")
    if email is None:
        flash("Link de recuperação inválido.", "danger")
        return redirect("/esqueci_a_senha")

    if request.method == "GET":
        return render_template("mudar_senha.html", token=token)

    nova_senha = request.form.get("senha")
    nova_senha_confirmar = request.form.get("senha_confirmar")

    if not nova_senha or not nova_senha_confirmar:
        flash("Preencha todos os campos.", "danger")
        return redirect(f"/mudar_senha/{token}")

    if nova_senha != nova_senha_confirmar:
        flash("As senhas não coincidem.", "danger")
        return redirect(f"/mudar_senha/{token}")

    # Atualiza senha
    moderador = Moderador.query.filter_by(email=email).first()
    if not moderador:
        flash("Usuário não encontrado.", "danger")
        return redirect("/esqueci_a_senha")

    moderador.senha_hash = generate_password_hash(nova_senha)
    try:
        db.session.commit()
        flash("Senha alterada com sucesso!", "success")
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar nova senha: {e}")
        flash("Erro ao atualizar senha. Tente novamente.", "danger")

    return redirect("/")
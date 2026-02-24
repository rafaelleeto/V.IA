from flask import Blueprint, request, render_template, redirect, session, flash, jsonify, url_for
from modelos import Moderador
from sqlalchemy import desc, or_


admin_blueprint = Blueprint(
    "admin", __name__, template_folder="../vistas/templates")


@admin_blueprint.before_request
def admin_before_request():
    if session.get("usuario") is None:
        flash("Você não está logado", "danger")
        return redirect("/")
    moderador = Moderador.query.filter_by(id=session.get("usuario")).first()
    print(moderador.nome)
    if moderador.admin == False:
        flash("Você não tem permissões", "danger")
        return redirect("/painel")


@admin_blueprint.route("/painel/admin")
def painel_admin():
    return render_template("admin.html")


@admin_blueprint.route("/painel/admin/ver_moderadores/<int:pagina>", methods=["GET", "POST"])
def painel_ver_moderadores(pagina):
    if request.method == "GET":
        moderadores = (
            Moderador.query
            .order_by(desc(Moderador.id))
            .paginate(
                page=pagina,
                per_page=10,
                error_out=False
            )
        )

        return render_template(
            "ver_moderadores.html",
            moderadores=moderadores,
            page=pagina
        )


@admin_blueprint.put("/htmx/editar_moderador/<int:id>")
def editar_moderador(id):
    moderador = Moderador.query.get_or_404(id)

    moderador.nome = request.form.get("nome")
    moderador.admin = request.form.get("admin") == "1"
    moderador.ativo = request.form.get("ativo") == "1"
    if moderador.admin == 0 or moderador.ativo == 0:
        if moderador.id == session["usuario"]:
            moderador.admin = True
            moderador.ativo = True
            moderador.salvar()
            html_moderador = render_template(
            "componentes/linha_moderador.html", moderador=moderador)
            html_mensagem = render_template(
            "componentes/mensagem.html",
            mensagens=[
                ("warning","Você não pode tirar suas próprias permissões")]
            )
            return html_moderador + html_mensagem
    moderador.salvar()

    html_moderador = render_template(
        "componentes/linha_moderador.html", moderador=moderador)
    html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("success", f"Informações do moderador {moderador.nome} atualizadas com sucesso.")]
    )
    return html_moderador + html_mensagem


@admin_blueprint.route("/painel/admin/criar_moderador", methods=["GET", "POST"])
def painel_criar_moderador():
    if request.method == "GET":
        return render_template("criar_moderador.html")

    nome = request.form["nome"]
    email = request.form["email"]
    checkbox = request.form.get("administrador", "0") == "1"

    if Moderador.query.filter_by(email=email).first():
        flash("Esse moderador já existe", "warning")
        return redirect("/painel/admin/criar_moderador")
    moderador = Moderador(
        nome=nome,
        email=email,
        senha_hash="",
        admin=checkbox,
        ativo=True
    )
    moderador.salvar()
    flash(f"Moderador {nome} criado com sucesso", "success")
    return redirect("/painel/admin/ver_moderadores/1")


@admin_blueprint.route("/htmx/buscar_moderadores")
def buscar_moderadores():
    pesquisa = request.args.get("nome", "").strip()
    busca = f"%{pesquisa}%"

    moderadores_filtrados = (
        Moderador.query
        .filter(
            or_(
                Moderador.nome.ilike(busca),
                Moderador.email.ilike(busca)
            )
        )
        .order_by(desc(Moderador.id))
        .paginate(per_page=10, error_out=False)
    )

    return render_template(
        "componentes/moderadores_body.html",
        moderadores=moderadores_filtrados
    )

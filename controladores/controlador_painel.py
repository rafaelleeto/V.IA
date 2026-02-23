from flask import Blueprint, request, render_template, redirect, session, flash, jsonify, json
from modelos import Moderador, Cliente, Cartao, Acesso
from datetime import date, datetime, timedelta
from sqlalchemy import func, or_, desc


painel_blueprint = Blueprint(
    "painel", __name__, template_folder="../vistas/templates")


@painel_blueprint.before_request
def painel_before_request():
    if session.get("usuario") is None:
        return redirect("/")


@painel_blueprint.route("/painel")
def painel_home():
    moderador = Moderador.query.get_or_404(session["usuario"])
    quantidade_moderadores = len(Moderador.query.all())
    quantidade_clientes = len(Cliente.query.filter_by(tem_acesso=True).all())
    quantidade_cartoes = len(Cartao.query.filter_by(tem_acesso=True).all())
    acessos_hoje = len(Acesso.query.filter(
        func.date(Acesso.data_criacao) == date.today()).all())
    return render_template("home.html", moderador=moderador, quantidade_moderadores=quantidade_moderadores,
                           quantidade_clientes=quantidade_clientes, quantidade_cartoes=quantidade_cartoes, acessos_hoje=acessos_hoje)


@painel_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@painel_blueprint.route("/painel/historico/<int:pagina>", methods=["GET", "POST"])
def painel_historico(pagina):
    if request.method == "GET":
        clientes = Cliente.query.all()
        acessos = Acesso.query.order_by(Acesso.id.desc()).paginate(
            per_page=10,
            page=pagina,
            error_out=False
        )
        mapa_cliente = {cliente.id: cliente for cliente in clientes}
        return render_template("historico.html", acessos=acessos, page=pagina, mapa_cliente=mapa_cliente, clientes=clientes)


@painel_blueprint.route("/painel/cartoes/<int:pagina>", methods=["GET", "POST"])
def painel_cartao(pagina):
    if request.method == "GET":
        cartoes = Cartao.query.order_by(desc(Cartao.id)).paginate(
            page=pagina,
            per_page=10,
            error_out=False
        )
        clientes = Cliente.query.all()
        mapa_cartao = {cliente.id: cliente for cliente in clientes}
        cartao = Cartao.query.all()
        clientes_ativos = Cliente.query.filter_by(tem_acesso=True).all()
        ids_com_cartao = {c.dono_id for c in cartao}
        clientes_ativos = [
            cliente for cliente in clientes_ativos
            if cliente.id not in ids_com_cartao
        ]
        return render_template("cartoes.html", cartoes=cartoes, page=pagina, mapa_cartao=mapa_cartao, clientes=clientes, clientes_ativos=clientes_ativos)


@painel_blueprint.route("/painel/clientes/<int:pagina>")
def painel_clientes(pagina):
    clientes = Cliente.query.order_by(Cliente.id.desc()).paginate(
        page=pagina, per_page=6, error_out=False)
    return render_template("ver_clientes.html", clientes=clientes, page=pagina)


@painel_blueprint.put("/htmx/editar_cliente/<int:id>")
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    cliente.nome = request.form.get("nome")
    cliente.documento = request.form.get("documento")
    cliente.tipo = request.form.get("tipo")
    cliente.tem_acesso = "tem_acesso" in request.form
    cliente.documento_valido = "documento_valido" in request.form

    cliente.salvar()

    html_cliente = render_template(
        "componentes/card_cliente_unico.html", cliente=cliente)

    html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("info", f"Cliente {cliente.nome} atualizado com sucesso.")])
    return html_cliente + html_mensagem


@painel_blueprint.route("/htmx/buscar_clientes")
def buscar_clientes():
    pesquisa = request.args.get("nome", "").strip()
    busca = f"%{pesquisa}%"
    clientes_filtrados = (
        Cliente.query
        .filter(
            or_(
                Cliente.nome.ilike(busca),
                Cliente.email.ilike(busca),
                Cliente.documento.ilike(busca),
                Cliente.tipo.ilike(busca),
            )
        )
        .order_by(Cliente.id.desc())
        .paginate(per_page=6)
    )

    return render_template("componentes/card_cliente.html", clientes=clientes_filtrados)


@painel_blueprint.get("/htmx/busca_acesso")
def buscar_acesso():
    pesquisa = request.args.get("pesquisa", "").strip()
    busca = f"%{pesquisa}%"
    mapa_cliente = {cliente.id: cliente for cliente in Cliente.query.all()}
    clientes = Cliente.query.filter(Cliente.nome.ilike(busca)).all()
    ids_clientes = [c.id for c in clientes]

    acessos_filtrados = (
        Acesso.query
        .order_by(Acesso.id.desc())
        .filter(
            or_(
                Acesso.usuario_id.in_(ids_clientes),
                Acesso.local.ilike(busca),
                Acesso.tipo_acesso.ilike(busca),
            )
        )
        .paginate(
            per_page=10,
            error_out=False
        )
    )

    return render_template(
        "componentes/historico_acesso.html",
        acessos=acessos_filtrados,
        mapa_cliente=mapa_cliente
    )


@painel_blueprint.post("/htmx/adicionar_cliente")
def adicionar_cliente():
    nome = request.form["nome"]
    email = request.form["email"]
    documento = request.form["documento"]
    tipo = request.form["tipo"]

    if Cliente.query.filter_by(email=email).first() or Cliente.query.filter_by(documento=documento).first():
        clientes_totais = Cliente.query.order_by(
            Cliente.id.desc()).paginate(per_page=6, error_out=False)
        html_card_cliente = render_template(
            "componentes/card_cliente.html", clientes=clientes_totais)
        html_mensagem = render_template(
            "componentes/mensagem.html", mensagens=[('danger', 'Esse cliente já está cadastrado.')])
        return html_card_cliente + html_mensagem

    cliente = Cliente(
        nome=nome,
        email=email,
        tem_acesso=True,
        tipo=tipo,
        documento=documento
    )
    cliente.salvar()
    html_mensagem = render_template(
        "componentes/mensagem.html", mensagens=[('success', f'Cliente {cliente.nome} adicionado com sucesso.')])
    clientes_totais = Cliente.query.order_by(
        Cliente.id.desc()).paginate(per_page=6, error_out=False)
    html_card_cliente = render_template(
        "componentes/card_cliente.html", clientes=clientes_totais)
    return html_card_cliente + html_mensagem


@painel_blueprint.post("/htmx/adicionar_registro")
def adicionar_registro():
    id = request.form["seletor"]
    local = request.form["seletor_tipo"]
    cliente = Cliente.query.get_or_404(id)

    acesso = Acesso(
        usuario_id=id,
        local="Manual - Paula Gomes",
        cartao_id=211,
        tipo_acesso=local,

    )
    acesso.salvar()
    acessos = Acesso.query.order_by(Acesso.id.desc()).paginate(per_page=10)
    acesso.salvar()
    mapa_cliente = mapa_cliente = {
        cliente.id: cliente for cliente in Cliente.query.all()}
    html_historico = render_template(
        "componentes/historico_acesso.html",
        acessos=acessos,
        mapa_cliente=mapa_cliente
    )
    html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("success", f"Acesso do cliente {cliente.nome} registrado com sucesso.")]
    )
    return html_historico + html_mensagem


from sqlalchemy import or_

@painel_blueprint.get("/htmx/busca_cartao")
def buscar_cartao():
    pesquisa = request.args.get("pesquisa", "").strip()
    busca = f"%{pesquisa}%"

    page = request.args.get("page", 1, type=int)

    clientes_por_nome = Cliente.query.filter(
        Cliente.nome.ilike(busca)
    ).all()

    ids_clientes = [c.id for c in clientes_por_nome]

    cartoes_filtrados = Cartao.query.filter(
        or_(
            Cartao.dono_id.in_(ids_clientes),
            Cartao.chave_cartao.ilike(busca)
        )
    ).order_by(Cartao.id.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    clientes = Cliente.query.order_by(Cliente.nome).all()

    mapa_cartao = {c.id: c for c in clientes}

    return render_template(
        "componentes/cartao_body.html",
        cartoes=cartoes_filtrados,
        clientes=clientes,
        mapa_cartao=mapa_cartao
    )


@painel_blueprint.route("/htmx/editar_cartao/<int:cartao_id>", methods=["PUT"])
def editar_cartao(cartao_id):
    cartao = Cartao.query.get_or_404(cartao_id)
    try:
        dono_id = request.form.get("dono_id", "").strip()
        chave_cartao = request.form.get("chave_cartao", "").strip()
        tem_acesso = 'tem_acesso' in request.form
        existe = Cartao.query.filter_by(dono_id=dono_id).first()
        clientes = Cliente.query.all()
        mapa_cartao = {cliente.id: cliente for cliente in clientes}
        if existe:
            html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("warning", f"Usuário já tem um cartão.")]
            )

            html_htmx = render_template("componentes/cartao_unico.html",
                               cartao=cartao,
                               mapa_cartao=mapa_cartao,
                               clientes=clientes)
            return html_htmx+html_mensagem



        if dono_id:
            cartao.dono_id = int(dono_id)
        if chave_cartao:
            cartao.chave_cartao = chave_cartao
        cartao.tem_acesso = tem_acesso

        cartao.salvar()


        html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("success", f"Acesso do cliente registrado com sucesso.")]
    )

        html_htmx = render_template("componentes/cartao_unico.html",
                               cartao=cartao,
                               mapa_cartao=mapa_cartao,
                               clientes=clientes)
        return html_htmx+html_mensagem

    except Exception as e:
        print("Erro ao editar cartão:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@painel_blueprint.route('/cartao/<int:cartao_id>/limpar', methods=['POST'])
def limpar_cartao(cartao_id):
    cartao = Cartao.query.get(cartao_id)
    cartao.tem_acesso = False
    cartao.dono_id = None
    cartao.salvar()
    
    html_mensagem = render_template(
        "componentes/mensagem.html",
        mensagens=[
            ("success", f"Cartão limpo com sucesso.")]
    )
    html_htmx = render_template('componentes/cartao_unico.html', cartao=cartao)
    return html_htmx + html_mensagem
    

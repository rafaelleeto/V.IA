from flask import Blueprint, request, render_template, jsonify, session
from modelos import Cartao, Acesso, Cliente
from datetime import datetime
from extensoes import socketio

api_blueprint = Blueprint(
    "api",
    __name__,
    template_folder="../vistas/templates"
)


@api_blueprint.route("/api_cartao", methods=["POST"])
def api_cartao():
    acesso_antigo = None

    try:
        cartao_info = request.get_json()

        if not cartao_info or "uid" not in cartao_info:
            return jsonify({
                "status": "erro",
                "mensagem": "JSON inválido"
            }), 400

        cartao_id = cartao_info["uid"]

        cartao_encontrado = Cartao.query.filter_by(
            chave_cartao=cartao_id
        ).first()

        acesso_antigo = (
            Acesso.query
            .filter_by(cartao_id=cartao_id)
            .order_by(Acesso.id.desc())
            .first()
        )

        # =============================
        # CARTÃO JÁ EXISTE
        # =============================
        if cartao_encontrado:

            cliente = Cliente.query.filter_by(
                id=cartao_encontrado.dono_id
            ).first()

            nome_cliente = cliente.nome if cliente else "Usuário não identificado"

            if not cartao_encontrado.tem_acesso:
                mensagens = [
                    ("danger", f"Acesso bloqueado! {nome_cliente}")
                ]

                html_alerta = render_template(
                    "componentes/mensagem.html",
                    mensagens=mensagens
                )

                socketio.emit(
                    'novo_alerta',
                    {'html': html_alerta},
                    namespace='/admin'
                )

                return jsonify({
                    "status": "negado",
                    "mensagem": "Acesso bloqueado"
                }), 403

            if not acesso_antigo or acesso_antigo.tipo_acesso == "Saída":
                entrada_ou_saida = "Entrada"
            else:
                entrada_ou_saida = "Saída"

            acesso = Acesso(
                usuario_id=cartao_encontrado.dono_id,
                cartao_id=cartao_id,
                tipo_acesso=entrada_ou_saida,
                local="Rua Paula Gomes"
            )
            acesso.salvar()

            hora_agora = datetime.now().hour

            if hora_agora < 12:
                saudacao = "Bom dia"
            elif hora_agora < 18:
                saudacao = "Boa tarde"
            else:
                saudacao = "Boa noite"

            mensagens = [
                ("success", f"{nome_cliente} - {entrada_ou_saida} autorizada")
            ]

            html_alerta = render_template(
                "componentes/mensagem.html",
                mensagens=mensagens
            )

            socketio.emit(
                'novo_alerta',
                {'html': html_alerta},
                namespace='/admin'
            )

            return jsonify({
                "status": "ok",
                "mensagem": f"{saudacao} {nome_cliente} - Acesso liberado",
                "tipo": entrada_ou_saida
            }), 200

        # =============================
        # CARTÃO NOVO
        # =============================
        mensagens = [
            ("warning", f"Novo cartão registrado: {cartao_id}")
        ]

        html_alerta = render_template(
            "componentes/mensagem.html",
            mensagens=mensagens
        )

        socketio.emit(
            'novo_alerta',
            {'html': html_alerta},
            namespace='/admin'
        )

        cartao = Cartao(
            dono_id=None,
            chave_cartao=cartao_id,
            tem_acesso=False
        )
        cartao.salvar()

        return jsonify({
            "status": "negado",
            "mensagem": "Cartão registrado, acesso bloqueado"
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Acesso antigo:", acesso_antigo)

        return jsonify({
            "status": "erro",
            "mensagem": "Erro interno no servidor"
        }), 500


@socketio.on('connect', namespace='/admin')
def connect_admin():
    print("Cartão On")


@socketio.on('disconnect', namespace='/admin')
def disconnect_admin():
    print("Cartão off")
from flask import Blueprint, request, render_template, redirect, session, flash, jsonify
from modelos import Cartao, Acesso, Cliente
from datetime import *


api_blueprint = Blueprint(
    "api", __name__, template_folder="../vistas/templates")


@api_blueprint.route("/api_cartao", methods=["POST"])
def api_cartao():
    try:
        cartao_info = request.get_json()
        if not cartao_info or "uid" not in cartao_info:
            return jsonify({"status": "erro", "mensagem": "JSON inválido"}), 400

        cartao_id = cartao_info["uid"]
        cartao_encontrado = Cartao.query.filter_by(
            chave_cartao=cartao_id).first()
        acesso_antigo = (
            Acesso.query
            .filter_by(cartao_id=cartao_id)
            .order_by(Acesso.id.desc())
            .first()
        )
        

        if cartao_encontrado:
            if cartao_encontrado.tem_acesso:
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
                cliente = Cliente.query.filter_by(
                    id=cartao_encontrado.dono_id).first()
                if hora_agora < 12:
                    mensagem = f"Bom dia {cliente.nome} - Acesso Liberado"
                    return jsonify({"status": "ok", "mensagem": mensagem}), 200
                elif hora_agora > 12 and hora_agora < 18:
                    mensagem = f"Boa Tarde {cliente.nome} - Acesso Liberado"
                    return jsonify({"status": "ok", "mensagem": mensagem}), 200
                else:
                    mensagem = f"Boa Noite {cliente.nome} - Acesso Liberado"
                    return jsonify({"status": "ok", "mensagem": mensagem}), 200

            else:
                return jsonify({"status": "negado", "mensagem": "Acesso bloqueado"}), 403
        else:
            cartao = Cartao(
                dono_id=None,
                chave_cartao=cartao_id,
                tem_acesso=False
            )
            cartao.salvar()
            return jsonify({"status": "negado", "mensagem": "Cartão registrado, acesso bloqueado"}), 403

    except Exception as e:
        print("Erro na rota /api_cartao:", e)
        print("Acesso antigo:", acesso_antigo)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

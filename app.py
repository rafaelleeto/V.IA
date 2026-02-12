from flask import Flask
from flask_migrate import Migrate
from config import Config
from modelos.modelo import db
from modelos import *
from controladores.controlador_principal import principal_blueprint
from controladores.controlador_painel import painel_blueprint
from controladores.controlador_admin import admin_blueprint
from controladores.controlador_dashboard import dashboard_blueprint
from controladores.controlador_api import api_blueprint
from extensoes import mail

app = Flask(__name__)

app.config.from_object(Config)
mail.init_app(app)

# Banco de dados + migração
db.init_app(app)
migrate = Migrate(app, db)

# Registra as blueprints
app.register_blueprint(principal_blueprint)
app.register_blueprint(painel_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(api_blueprint)


def preguiça():
    for i in range(30):
        nome = "preguicinha"
        email = f"paulo{i+1}@gmail.com"
        novo = Moderador(
            nome=nome,
            email=email,
            senha_hash="teste123",
            admin=False,
            ativo=True
        )

        novo.salvar()
        print("Contas criadas")


def preguiça_2():
    for i in range(30):
        novo = Cartao(
            dono_id=1,
            chave_cartao=i+1,
            tem_acesso=True
        )

        novo.salvar()
        print("Cartões criadas")


def preguiça_3():
    for i in range(30):
        novo = Acesso(
            usuario_id=i+1,
            cartao_id=i+1,
            tipo_acesso="entrada",
            local="Garagem"
        )
        novo.salvar()
        print("Acessos criados")


def preguiça_4():
    for i in range(30):
        novo = Cliente(
            nome="rafa",
            documento=i+1,
            tem_acesso=1,
            tipo="Aluno",
            email=f"paulo{i+1}@gmail.com"
        )
        novo.salvar()
        print("Clientes criados")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

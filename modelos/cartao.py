from modelos.modelo import Modelo, db


class Cartao(Modelo):
    __tablename__ = "cartoes"

    dono_id = db.Column(db.Integer, nullable=True)
    chave_cartao = db.Column(db.String(120), nullable=False, unique=True)
    tem_acesso = db.Column(db.Boolean, nullable=False)

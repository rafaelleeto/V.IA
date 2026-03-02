from modelos.modelo import db, Modelo


class Acesso(Modelo):
    __tablename__ = "acessos"

    usuario_id = db.Column(db.Integer, nullable=True)
    cartao_id = db.Column(db.String(40), nullable=False)
    tipo_acesso = db.Column(db.String(120), nullable=True)
    local = db.Column(db.String(120), nullable=True)
    liberado_ou_bloqueado = db.Column(db.Boolean, nullable=False)
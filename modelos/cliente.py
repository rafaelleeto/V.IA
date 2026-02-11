from modelos.modelo import db, Modelo


class Cliente(Modelo):
    __tablename__ = "clientes"

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    documento = db.Column(db.String(120), unique=True, nullable=False)
    tem_acesso = db.Column(db.Boolean, nullable=False)
    tipo = db.Column(db.String(120), nullable=False)

    def verificar_usuario(self):
        pass

    def validar_acesso(self):
        pass

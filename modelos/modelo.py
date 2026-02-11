from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Modelo(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(
        db.DateTime, default=datetime.now, nullable=False)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def atualizar(self):
        db.session.commit()

    # Transaforma em json para a API

    @property
    def json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

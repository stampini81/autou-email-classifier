from datetime import datetime
from app_v2 import db


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

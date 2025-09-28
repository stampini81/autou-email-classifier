from flask_sqlalchemy import SQLAlchemy
# ...existing code...
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
db = SQLAlchemy(app)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())

# ...existing code...

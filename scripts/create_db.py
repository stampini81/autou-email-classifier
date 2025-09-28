from app_v2 import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("DB inicializado (tabelas criadas).")

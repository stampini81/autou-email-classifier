from app_v2 import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from app_v2 import models
        models.db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)

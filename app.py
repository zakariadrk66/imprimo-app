# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)  # ✅ Initialisation ici
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # ✅ Importer les modèles APRÈS db.init_app(app)
    from models import User, Order, AuditLog  # 👈 Important !

    from routes import main
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Tables créées avec succès !")
    app.run(debug=True)
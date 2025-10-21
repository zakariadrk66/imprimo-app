# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    #  ✅ Définir le user_loader ici
    @login_manager.user_loader
    def load_user(user_id):
        # ⚠️ CORRIGÉ : Utiliser db.session.get au lieu de User.query.get
        from models import User
        return db.session.get(User, int(user_id))

    db.init_app(app)

    from models import User, Order, AuditLog
    from routes import main
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Tables créées avec succès !")
    app.run(debug=True)
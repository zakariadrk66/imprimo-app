# seed.py
from app import create_app, db
from models import User
import hashlib

def create_users():
    app = create_app()
    with app.app_context():
        # Créer un utilisateur admin
        admin = User.query.filter_by(email="admin@imprimo.com").first()
        if not admin:
            admin = User(
                email="admin@imprimo.com",
                role="admin",
                bw_quota=1000,
                color_quota=500
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("✅ Admin créé : admin@imprimo.com / admin123")

        # Créer un utilisateur agent
        agent = User.query.filter_by(email="agent@imprimo.com").first()
        if not agent:
            agent = User(
                email="agent@imprimo.com",
                role="agent",
                bw_quota=800,
                color_quota=400
            )
            agent.set_password("agent123")
            db.session.add(agent)
            print("✅ Agent créé : agent@imprimo.com / agent123")

        # Créer un utilisateur final
        user = User.query.filter_by(email="user@imprimo.com").first()
        if not user:
            user = User(
                email="user@imprimo.com",
                role="user",
                bw_quota=500,
                color_quota=200
            )
            user.set_password("user123")
            db.session.add(user)
            print("✅ Utilisateur créé : user@imprimo.com / user123")

        db.session.commit()
        print("✅ Tous les utilisateurs ont été créés avec succès !")

if __name__ == "__main__":
    create_users()
# app.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'

    @app.route('/')
    def home():
        return "<h1>Bienvenue sur Imprimo !</h1>"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
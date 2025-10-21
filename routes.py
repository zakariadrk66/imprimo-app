# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm
import hashlib

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.password == hashlib.sha256(password.encode()).hexdigest():
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'error')

    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin/dashboard.html')
    elif current_user.role == 'agent':
        return render_template('agent/dashboard.html')
    else:
        return render_template('user/dashboard.html')

# Fonction pour charger l'utilisateur (requis par Flask-Login)
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Order, AuditLog
from forms import LoginForm, OrderForm
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

        if user and user.check_password(password):
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

# ✅ Nouvelles routes pour les fonctionnalités de base
@main.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@main.route('/orders')
@login_required
def orders_history():
    if current_user.role != 'agent':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))
    
    orders = Order.query.all()
    return render_template('agent/orders.html', orders=orders)

@main.route('/user/orders')
@login_required
def user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('user/orders.html', orders=orders)

@main.route('/import-users')
@login_required
def import_users():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/import_users.html')


    
    # Logique d'import CSV à implémenter dans l'étape suivante
    flash('Import CSV en cours de développement', 'info')
    return redirect(url_for('main.import_users'))

# routes.py

@main.route('/audit-log')
@login_required
def audit_log():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))
    
    logs = AuditLog.query.all()
    return render_template('admin/audit_log.html', logs=logs)

 # ✅ Nouvelle route pour créer une commande
@main.route('/create-order', methods=['GET', 'POST'])
@login_required
def create_order():
    if current_user.role != 'agent':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))

    form = OrderForm()
    if form.validate_on_submit():
        # Trouver l'utilisateur par email
        user = User.query.filter_by(email=form.user_email.data).first()
        if not user:
            flash('Utilisateur non trouvé', 'error')
            return render_template('agent/create_order.html', form=form)

        # Calculer l'utilisation actuelle pour le mois
        from datetime import datetime
        current_month_orders = Order.query.filter(
            Order.user_id == user.id,
            db.extract('month', Order.created_at) == datetime.now().month,
            db.extract('year', Order.created_at) == datetime.now().year
        ).all()

        total_bw_used = sum(o.bw_copies for o in current_month_orders) + form.bw_copies.data
        total_color_used = sum(o.color_copies for o in current_month_orders) + form.color_copies.data

        # Vérifier les quotas
        if total_bw_used > user.bw_quota:
            flash('Quota Noir & Blanc dépassé', 'error')
            return render_template('agent/create_order.html', form=form)

        if total_color_used > user.color_quota:
            flash('Quota Couleur dépassé', 'error')
            return render_template('agent/create_order.html', form=form)

        # ✅ Vérifier l'alerte 80%
        bw_percentage = (total_bw_used / user.bw_quota) * 100 if user.bw_quota > 0 else 0
        color_percentage = (total_color_used / user.color_quota) * 100 if user.color_quota > 0 else 0

        if bw_percentage >= 80 or color_percentage >= 80:
            alert_msg = []
            if bw_percentage >= 80:
                alert_msg.append(f"Atteinte de {bw_percentage:.1f}% du quota Noir & Blanc")
            if color_percentage >= 80:
                alert_msg.append(f"Atteinte de {color_percentage:.1f}% du quota Couleur")
            flash("⚠️ " + " et ".join(alert_msg), 'warning')

        # ✅ Créer la commande
        order = Order(
            user_id=user.id,
            agent_id=current_user.id,
            bw_copies=form.bw_copies.data,
            color_copies=form.color_copies.data
        )
        db.session.add(order)
        db.session.commit()
        
     

        flash('Commande créée avec succès', 'success')
        return redirect(url_for('main.orders_history'))

    return render_template('agent/create_order.html', form=form)

# ✅ Nouvelle route pour modifier les quotas
@main.route('/update-quota/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_quota(user_id):
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))

    user = db.session.get(User, user_id)  # ✅ Utiliser db.session.get (compatible SQLAlchemy 2.0)
    if not user:
        flash('Utilisateur non trouvé', 'error')
        return redirect(url_for('main.users'))

    if request.method == 'POST':
        bw_quota = request.form.get('bw_quota', type=int)
        color_quota = request.form.get('color_quota', type=int)

        if bw_quota is not None and color_quota is not None:
            user.bw_quota = bw_quota
            user.color_quota = color_quota
            db.session.commit()
            flash(f'Quotas de {user.email} mis à jour', 'success')
            log_action(current_user, 'UPDATE_QUOTA', {'user_id': user.id, 'bw': bw_quota, 'color': color_quota})
            return redirect(url_for('main.users'))

    return render_template('admin/update_quota.html', user=user)

# Fonction utilitaire pour journaliser les actions
def log_action(user, action, details):
    log = AuditLog(user_id=user.id, action=action, details=details)
    db.session.add(log)
    db.session.commit()
    
# ✅ Nouvelle route pour importer des utilisateurs via CSV
@main.route('/upload-csv', methods=['POST'])
@login_required
def upload_csv():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))

    file = request.files.get('csv_file')
    if not file or file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('main.import_users'))

    if not file.filename.endswith('.csv'):
        flash('Format de fichier invalide. CSV requis.', 'error')
        return redirect(url_for('main.import_users'))

    import csv
    import re
    errors = []
    successes = 0

    # Lire le contenu du fichier
    content = file.read().decode('utf-8').splitlines()
    reader = csv.reader(content)

    for line_num, row in enumerate(reader, start=1):
        if len(row) != 3:
            errors.append(f"Ligne {line_num}: Format invalide (3 colonnes requises)")
            continue

        email, bw_str, color_str = row

        # Valider l'email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append(f"Ligne {line_num}: Email invalide ({email})")
            continue

        # Valider les quotas
        try:
            bw = int(bw_str)
            color = int(color_str)
            if bw <= 0 or color <= 0:
                errors.append(f"Ligne {line_num}: Quotas doivent être positifs ({bw}, {color})")
                continue
        except ValueError:
            errors.append(f"Ligne {line_num}: Quotas doivent être des nombres ({bw_str}, {color_str})")
            continue

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Mettre à jour les quotas
            existing_user.bw_quota = bw
            existing_user.color_quota = color
            log_action(current_user, 'UPDATE_QUOTA', {'user_id': existing_user.id, 'bw': bw, 'color': color})
            successes += 1
        else:
            # Créer un nouvel utilisateur
            new_user = User(email=email, role='user', bw_quota=bw, color_quota=color)
            new_user.set_password('password123')  # Mot de passe par défaut
            db.session.add(new_user)
            log_action(current_user, 'CREATE_USER', {'email': email, 'bw': bw, 'color': color})
            successes += 1

    if successes > 0:
        db.session.commit()
        flash(f'Import terminé : {successes} utilisateurs traités.', 'success')

    if errors:
        for error in errors:
            flash(error, 'error')

    return redirect(url_for('main.import_users'))

@main.route('/enable-2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        current_user.enable_2fa()
        db.session.commit()
        flash('2FA activé avec succès', 'success')
        return redirect(url_for('main.dashboard'))

    # Générer un QR code pour l'application d'authentification
    totp_uri = pyotp.totp.TOTP(current_user.two_fa_secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Imprimo"
    )
    return render_template('admin/enable_2fa.html', totp_uri=totp_uri)

# ✅ Nouvelle route pour désactiver le 2FA
@main.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('main.dashboard'))

    current_user.is_2fa_enabled = False
    db.session.commit()
    flash('2FA désactivé', 'info')
    return redirect(url_for('main.dashboard'))


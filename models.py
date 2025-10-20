# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'agent', 'user'
    bw_quota = db.Column(db.Integer, default=0)
    color_quota = db.Column(db.Integer, default=0)
    password = db.Column(db.String(200), nullable=False)
    two_fa_secret = db.Column(db.String(32), nullable=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bw_copies = db.Column(db.Integer, nullable=False)
    color_copies = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # Ex: 'CREATE_ORDER'
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())
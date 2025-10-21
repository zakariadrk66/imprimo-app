# models.py
from extensions import db
from sqlalchemy import func
from flask_login import UserMixin
import hashlib
import pyotp 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'agent', 'user'
    bw_quota = db.Column(db.Integer, default=0)
    color_quota = db.Column(db.Integer, default=0)
    password = db.Column(db.String(200), nullable=False)
    two_fa_secret = db.Column(db.String(32), nullable=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()

 # ✅ Méthodes pour la gestion du 2FA
    def enable_2fa(self):
        if not self.two_fa_secret:
            self.two_fa_secret = pyotp.random_base32()
        self.is_2fa_enabled = True

    def verify_2fa(self, token):
        if not self.is_2fa_enabled or not self.two_fa_secret:
            return False
        totp = pyotp.TOTP(self.two_fa_secret)
        return totp.verify(token)

    # Relations inversées pour Order
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='user_obj')
    created_orders = db.relationship('Order', foreign_keys='Order.agent_id', backref='agent_obj')
    
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
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())
# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

# ✅ Nouveau formulaire pour créer une commande
class OrderForm(FlaskForm):
    user_email = StringField('Email de l\'utilisateur', validators=[DataRequired(), Email()])
    bw_copies = IntegerField('Copies Noir & Blanc', validators=[NumberRange(min=0)])
    color_copies = IntegerField('Copies Couleur', validators=[NumberRange(min=0)])
    submit = SubmitField('Créer la commande')
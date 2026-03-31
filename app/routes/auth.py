from flask import render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.routes import auth
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask import Blueprint
import requests
import os

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form, google_client_id=GOOGLE_CLIENT_ID)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            student_id=form.student_id.data,
            email=form.email.data,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered student!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form, google_client_id=GOOGLE_CLIENT_ID)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def _verify_google_token(token):
    try:
        resp = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': token}, timeout=5)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get('aud') != GOOGLE_CLIENT_ID:
            return None
        return data
    except Exception:
        return None

@auth.route('/google_login', methods=['POST'])
def google_login():
    data = request.get_json(silent=True)
    token = data.get('credential') if data else None
    if not token:
        return jsonify(success=False, message='No credential provided.'), 400
    google_data = _verify_google_token(token)
    if not google_data:
        return jsonify(success=False, message='Invalid Google token.'), 401
    email = google_data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(success=False, message='No account found with this email. Please register first.'), 404
    login_user(user, remember=True)
    return jsonify(success=True, redirect=url_for('main.dashboard'))

@auth.route('/google_register', methods=['POST'])
def google_register():
    data = request.get_json(silent=True)
    token = data.get('credential') if data else None
    if not token:
        return jsonify(success=False, message='No credential provided.'), 400
    google_data = _verify_google_token(token)
    if not google_data:
        return jsonify(success=False, message='Invalid Google token.'), 401
    email = google_data.get('email')
    name = google_data.get('name', '')
    existing = User.query.filter_by(email=email).first()
    if existing:
        login_user(existing, remember=True)
        return jsonify(success=True, redirect=url_for('main.dashboard'))
    return jsonify(success=True, fill_form=True, name=name, email=email)
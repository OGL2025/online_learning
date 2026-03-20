from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.routes import auth
from app.forms import LoginForm, RegistrationForm
from app.models import Student
from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student is None or not student.check_password(form.password.data):
            # Note: You need to implement check_password in the Model, or use werkzeug directly here
            # For simplicity in this file, I'll assume the password check method exists.
            # We will add this method to the Student model in a final polish if needed,
            # but for now, let's use werkzeug check_password_hash
            from werkzeug.security import check_password_hash
            if student is None or not check_password_hash(student.password_hash, form.password.data):
                flash('Invalid email or password')
                return redirect(url_for('auth.login'))
        
        login_user(student, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        student = Student(
            name=form.name.data,
            student_id=form.student_id.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(student)
        db.session.commit()
        flash('Congratulations, you are now a registered student!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
import requests
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.auth import auth_bp
from app.auth.forms import RegistrationForm, LoginForm
from app.models import User


def verify_hcaptcha(token):
    response = requests.post('https://hcaptcha.com/siteverify', data={
        'secret': current_app.config['HCAPTCHA_SECRET_KEY'],
        'response': token
    })
    return response.json().get('success', False)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('swipe.deck'))
    form = RegistrationForm()
    if form.validate_on_submit():
        token = request.form.get('h-captcha-response')
        if not verify_hcaptcha(token):
            flash('Please complete the captcha.', 'danger')
            return render_template('auth/register.html', form=form)
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_pw, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Complete your profile to start swiping.', 'success')
        return redirect(url_for('profiles.edit'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('swipe.deck'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('swipe.deck'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    session = db.session.session_factory() 
    user = session.query(User).filter_by(email=email).first()

    if (not user or user and not check_password_hash(user.password, password)):
        flash('Patikrinkite prisijungimo duomenis ir bandykite vėl.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    if (not email):
        flash('Neįvedėte naujo naudotojo elektroninio pašto adreso!')
        return redirect(url_for('auth.signup'))

    if (not name):
        flash('Neįvedėte naujo naudotojo vardo!')
        return redirect(url_for('auth.signup'))

    if (not password):
        flash('Neįvedėte naujo naudotojo slaptažodžio!')
        return redirect(url_for('auth.signup'))

    session = db.session.session_factory() 
    user = session.query(User).filter_by(email=email).first()

    if (user):
        flash('Naudotojas su tokiu elektroniniu paštu jau egzistuoja')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    session.add(new_user)
    session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import Users
from app.helpers.formDatabase import create_new_user_db
from . import db
from uuid import uuid4

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
    user = session.query(Users).filter_by(email=email).first()

    if (not user or user and not check_password_hash(user.password, password)):
        flash('Patikrinkite prisijungimo duomenis ir bandykite vėl.')
        return redirect(url_for('auth.login'))
    
    login_user(user, remember=remember)

    #sugeneruojam duombazę
    create_new_user_db(user, password)

    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    repeatPassword = request.form.get('repeatPassword')

    if (not email):
        flash('Neįvedėte naujo naudotojo elektroninio pašto adreso!')
        return redirect(url_for('auth.signup'))

    if (not name):
        flash('Neįvedėte naujo naudotojo vardo!')
        return redirect(url_for('auth.signup'))

    if (password != repeatPassword):
        flash('Slaptažodžiai nesutampa!')
        return redirect(url_for('auth.signup'))

    if (not password):
        flash('Neįvedėte naujo naudotojo slaptažodžio!')
        return redirect(url_for('auth.signup'))

    session = db.session.session_factory() 
    user = session.query(Users).filter_by(email=email).first()

    if (user):
        flash('Naudotojas su tokiu elektroniniu paštu jau egzistuoja!')
        return redirect(url_for('auth.signup'))
 
    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'), uuid=str(uuid4()))

    if (new_user.name == 'Admin' and session.query(Users).filter_by(name=new_user.name).first() is None):
        new_user.is_admin = True    

    session.add(new_user)      
    session.commit()        

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
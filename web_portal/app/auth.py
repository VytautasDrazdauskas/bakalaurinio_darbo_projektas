from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import Users, Test
from . import db, Session
from app.formDatabase import createNewDatabase
from flask.app import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import create_engine
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.types import String
from random import random

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

    db_name = user.uuid
    db_name = db_name.replace('-', '')
    user_sys_name = user.name.replace(' ','') + str(user.id)
    
    meta = MetaData()
    test_table = Table('test', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String(100))
    )

    #testing
    engine = create_engine('mysql+pymysql://root:MANOkompas123@localhost:3306/'+db_name)  
    Session.configure(bind=engine)
    sess = Session()

    new_test = Test(name='Test' + user_sys_name + str(random()))
    sess.add(new_test)
    sess.commit()  

    new_res = sess.query(Test).all()

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
    user = session.query(Users).filter_by(email=email).first()

    if (user):
        flash('Naudotojas su tokiu elektroniniu paštu jau egzistuoja')
        return redirect(url_for('auth.signup'))

    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    
    session.add(new_user)      
    session.commit()  

    createNewDatabase(new_user, password)


    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
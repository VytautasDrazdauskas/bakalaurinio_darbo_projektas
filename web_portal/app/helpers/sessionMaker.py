from sqlalchemy.engine import create_engine
from flask import  flash
from flask_login import current_user
from app.models import Users
from app import db, Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import create_engine
from unittest.mock import Base



def get_user_engine():
    if current_user.is_authenticated: 
        user_id = current_user.get_id()
    user = db.session.query(Users).get(int(user_id))
    db_name = user.uuid
    db_name = db_name.replace('-', '')  
    return create_engine('mysql+pymysql://dbupdate_user:DBupdate123@localhost:3306/db_'+db_name)

def create_user_session():    
    engine = get_user_engine()      
    Session.configure(bind=engine)
    return Session()

def table_exists(name):
    engine = get_user_engine()

    try:
        ret = engine.dialect.has_table(engine, name)
    except Exception as Ex:
        raise

    return ret

def create_table(table_object):
    engine = get_user_engine()

    try:
        Base.metadata.create_all(engine, tables=table_object)
    except Exception as Ex:
        raise
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from service.models import Users
import service.helpers.loadConfig as config

def get_user_db_name(user):
    db_name = user.uuid
    db_name = db_name.replace('-', '')

    return db_name

#schemos formavimo metodai
def table_exists(user,name):
    engine = create_user_engine(user)
    try:
        ret = engine.dialect.has_table(engine, name)
    except Exception as Ex:
        raise

    return ret

def create_table(table_object):
    engine = create_user_engine()
    try:
        Base.metadata.create_all(engine, tables=table_object)
    except Exception as Ex:
        raise

def create_user_engine(user):
    engine = create_engine('mysql+pymysql://'+config.db_user+':'+config.db_password+'@'+config.db_ip+':'+config.db_port+'/db_'+get_user_db_name(user))
    return engine

def create_user_session(user):
    engine = create_user_engine(user)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session
    
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import loadConfig as config

engine = create_engine('mysql+pymysql://'+config.db_user+':'+config.db_password+'@'+config.db_ip+':'+config.db_port+'/MainDB')
Session = sessionmaker(bind=engine)

Base = declarative_base()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import service.helpers.loadConfig as config

engine = create_engine('mysql+pymysql://'+config.database.user+':'+config.database.password+'@'+config.database.host+':'+config.database.port+'/MainDB')
Session = sessionmaker(bind=engine)

Base = declarative_base()
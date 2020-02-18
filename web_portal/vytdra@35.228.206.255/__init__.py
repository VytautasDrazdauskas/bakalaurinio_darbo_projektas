from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager 
import pymysql 
from werkzeug.utils import secure_filename
from queue import Queue
from app.logger import Logger
import app.load_config as app_config


UPLOAD_FOLDER = '/path/qrcodes'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy()
personal_db = SQLAlchemy()
pymysql.install_as_MySQLdb()
queue = Queue()
logger = Logger()

def create_app():   
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = '8a1wf-a846afw-vxxvf8-asfaf854'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+app_config.db_user+':'+app_config.db_password+'@'+app_config.db_ip+':'+app_config.db_port+'/MainDB?charset=utf8mb4'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = '123456789'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    #Suformuoja pagrindine db
    from app.models import Users, Devices
    from app.helpers.build_main_database import build_main_database
    with app.app_context():
        session = db.session.session_factory()
        build_main_database(session)

    if __name__== '__main__':
        app.run(debug=True,host='0.0.0.0',port='43210')

    return app
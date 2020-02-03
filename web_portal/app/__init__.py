from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager 
import pymysql 
from werkzeug.utils import secure_filename
from queue import Queue
import app.loadConfig as config


UPLOAD_FOLDER = '/path/qrcodes'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy()
personal_db = SQLAlchemy()
pymysql.install_as_MySQLdb()
queue = Queue()

def create_app():   
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = '8a1wf-a846afw-vxxvf8-asfaf854'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+config.db_user+':'+config.db_password+'@'+config.db_ip+':'+config.db_port+'/MainDB?charset=utf8mb4'
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
    from app.helpers.buildMainDb import BuildMainDb
    with app.app_context():
        session = db.session.session_factory()
        BuildMainDb(session)

    if __name__== '__main__':
        app.run(debug=True,host='0.0.0.0',port='43210')

    return app
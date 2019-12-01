from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager 
import pymysql 

db = SQLAlchemy()
pymysql.install_as_MySQLdb()

def create_app():   
    app = Flask(__name__)
    app.config['DEBUG'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dbupdate_user:DBupdate123@localhost:3306/MainDB'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123456789'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    if __name__== '__main__':
        app.run(debug=True,host='0.0.0.0',port='43210')

    return app
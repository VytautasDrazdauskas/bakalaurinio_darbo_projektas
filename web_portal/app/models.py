from flask_login import UserMixin
from . import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(200))
    uuid = db.Column(db.String(36), unique=True)

class UserDevices(db.Model):
    __tablename__ = "user_devices"

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    uuid = db.Column(db.String(36), unique=True)
    status = db.Column(db.Integer)
    device_type = db.Column(db.Integer)
    date_added_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_added_local = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Test(db.Model):
    __tablename__ = "test"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    
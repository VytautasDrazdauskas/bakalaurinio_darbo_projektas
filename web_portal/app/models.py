from flask_login import UserMixin
from . import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
import app.helpers.enums as enums
from sqlalchemy.ext.declarative import declared_attr

#--------------- MAIN DB --------------------------------------
class Users(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    assigned_devices = db.relationship("Devices", backref='user', lazy=True)
       
class Devices(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)    
    mac = db.Column(db.String(12), unique=True)
    uuid = db.Column(db.String(36), unique=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'), nullable=True)

#Rutininių darbų tvarkaraštis
class DeviceJobs(db.Model):
    __tablename__ = "device_jobs"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer,db.ForeignKey('devices.id'), nullable=False)
    start_time = db.Column(db.Numeric(8,2), nullable=False)
    finish_time = db.Column(db.Numeric(8,2), nullable=False)
    weekdays = db.Column(db.String(7))
    config_uuid = db.Column(db.String(36))

#---------------------------- USER DB ---------------------------------

class UserDevices(db.Model):
    __tablename__ = "user_devices"

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    mac = db.Column(db.String(12), unique=True)
    status = db.Column(db.Integer, default=0)
    date_added_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_added_local = db.Column(db.DateTime, nullable=False, default=datetime.now)
    device_type = db.Column(db.Integer, nullable=False, default=enums.DeviceType.Default.value)   

#--------------------------  Base models  ----------------------------------
class DeviceConfigBase(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(100), nullable=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)    
    weekdays = db.Column(db.String(7))
    start_time = db.Column(db.Numeric(8,2), nullable=False)
    finish_time = db.Column(db.Numeric(8,2), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modification_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @declared_attr
    def device_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user_devices.id'), nullable=False)

class DeviceDataBase(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)   
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @declared_attr
    def device_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user_devices.id'), nullable=False)
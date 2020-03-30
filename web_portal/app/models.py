from flask_login import UserMixin
from . import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
import app.helpers.enums as enums
from sqlalchemy.ext.declarative import declared_attr
from abc import abstractmethod
from uuid import uuid4

# --------------- MAIN DB --------------------------------------


class Users(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False)
    assigned_devices = db.relationship("Devices", backref='user', lazy=True)

    def __init__(self, email, name, password):
        self.uuid = str(uuid4())
        self.is_admin = False
        self.email = email
        self.name = name
        self.password = password


class Devices(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(12), unique=True)
    uuid = db.Column(db.String(36), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    aes_key_change_date = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, mac, user_id=None, aes_key_change_date=None):
        self.uuid = str(uuid4())
        self.mac = mac
        self.user_id = user_id
        self.aes_key_change_date = aes_key_change_date

# Rutininių darbų tvarkaraštis


class DeviceJobs(db.Model):
    __tablename__ = "device_jobs"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'devices.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    finish_date = db.Column(db.DateTime, nullable=True, default=None)
    weekdays = db.Column(db.String(7))
    config_uuid = db.Column(db.String(36))
    running = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, device_id, start_time, duration, weekdays, config_uuid, running):
        self.device_id = device_id
        self.start_time = start_time
        self.finish_time = None
        self.duration = duration
        self.weekdays = weekdays
        self.config_uuid = config_uuid
        self.running = running

# ---------------------------- USER DB ---------------------------------


class UserDevices(db.Model):
    __tablename__ = "user_devices"

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    mac = db.Column(db.String(12), unique=True)
    status = db.Column(db.Integer, default=enums.DeviceState.Registered.value)
    date_added_utc = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    date_added_local = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    device_type = db.Column(db.Integer, nullable=False)
    publish_interval = db.Column(db.Integer, nullable=False, default=30)
    aes_key_interval = db.Column(db.Integer, nullable=True)

    def __init__(self, device_name, mac, status, device_type, publish_interval, aes_key_interval):
        self.device_type = device_type
        self.status = status
        self.device_name = device_name
        self.mac = mac
        self.publish_interval = publish_interval
        self.aes_key_interval = aes_key_interval


class UserDeviceHistory(db.Model):
    __tablename__ = "user_device_history"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'user_devices.id'), nullable=False)
    text = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, device_id, text):
        self.device_id = device_id
        self.text = text

# --------------------------  Abstraktus baziniai modeliai  ----------------------------------

class DeviceConfigBase(db.Model):
    __abstract__ = True

    uuid = db.Column(db.String(36), primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    job_state = db.Column(db.Boolean, nullable=True, default=None)
    weekdays = db.Column(db.String(7), nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Time, nullable=True)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

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

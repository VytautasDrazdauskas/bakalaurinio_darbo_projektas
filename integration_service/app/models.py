from _datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship, backref
from helper.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    uuid = Column(String(36), nullable=False, unique=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    assigned_devices = relationship("Devices", backref='user', lazy=True)

class UserDevices(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True)
    device_name = Column(String(100))
    mac = Column(String(12), unique=True)
    status = Column(Integer)
    date_added_utc = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_added_local = Column(DateTime, nullable=False, default=datetime.now)
    led_state = Column(Boolean, nullable=False, default=False)    

class Devices(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)    
    mac = Column(String(12), unique=True)
    uuid = Column(String(36), unique=True)
    user_id=Column(Integer,ForeignKey('users.id'), nullable=True)
    data = relationship("DeviceData", backref='device', lazy=True)

class DeviceData(Base):
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True)
    device_id=Column(Integer,ForeignKey('devices.id'), nullable=False)
    temp = Column(Numeric(8,2), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
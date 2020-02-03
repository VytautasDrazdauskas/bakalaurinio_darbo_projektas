from app import db
from app.models import Users, Devices, DeviceJobs

def BuildMainDb(session):
    if not table_exists("users"):                 
        Users.__table__.create(session.bind)

    if not table_exists("devices"):                 
        Devices.__table__.create(session.bind)

    if not table_exists("device_jobs"):                 
        DeviceJobs.__table__.create(session.bind)

def table_exists(name):
    engine = db.engine

    try:
        ret = engine.dialect.has_table(engine, name)
    except Exception as Ex:
        raise

    return ret
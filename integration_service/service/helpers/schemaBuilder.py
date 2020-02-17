from service.helpers.base import Session, engine, Base

def table_exists(name):
        try:
            ret = engine.dialect.has_table(engine, name)
        except Exception as Ex:
            raise
        return ret
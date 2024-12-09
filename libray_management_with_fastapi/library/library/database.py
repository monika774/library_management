from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager

DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1:3306/LibraryDB"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        
def get_db():
    with get_session() as session:
        yield session
from sqlmodel import SQLModel, create_engine, Session
from backend import models

database_url = f"sqlite:///./chat.db"

engine = create_engine(database_url,echo=True)

def create_db_and_tables():
    print("DATABASE_PATH =", database_url)
    print("Tables connues par SQLModel :", SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine)
    with engine.connect() as conn:
        result = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        print("Tables réellement présentes dans SQLite :", result.fetchall())


def get_session():
    with Session(engine) as session:
        yield session
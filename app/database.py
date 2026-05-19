from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import time
# import psycopg
from psycopg.rows import dict_row
from .config import settings

SQLALCHEMY_DATBASE_URL = f"postgres://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATBASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# while True:
#     try:
#         conn = psycopg.connect("dbname=fastapi user=postgres password=admin123 host=localhost")
#         cursor = conn.cursor(row_factory=dict_row)
#         print("Database connection successful!")
#         break
#     except Exception as error:
#         print(f"Connecting to database failed : {error}")
#         time.sleep(2)
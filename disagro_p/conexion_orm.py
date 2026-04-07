import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

#el primer parametros es el driver
SERVER = os.environ.get("SERVER", "postgres")
DATABASE = os.environ.get("DATABASE", "disagro_db")
USERNAME = os.environ.get("USERNAME", "disagro")
PASSWORD = os.environ.get("PASSWORD", "disagro2024")
PUERTO = os.environ.get("PUERTO", "5432")


print("USERNAME:", USERNAME)
print("PASSWORD:", PASSWORD)
print("SERVER:", SERVER)
print("PUERTO:", PUERTO)
print("DATABASE:", DATABASE)

connection_url = URL.create(
    "postgresql+psycopg2",
    username=USERNAME,
    password=PASSWORD,
    host=SERVER,
    port=PUERTO,
    database=DATABASE
)

engine = create_engine(connection_url,pool_size=10,max_overflow=5,pool_timeout=30,pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


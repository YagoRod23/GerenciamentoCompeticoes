from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Esta linha é importante para definir o Base

def init_db():
    """
    Inicializa as tabelas do banco de dados.
    """
    Base.metadata.create_all(bind=engine)

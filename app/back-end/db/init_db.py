#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = "postgresql+psycopg2://postgres:liteonpostgres@10.1.14.89:5432/postgres"

engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    return db

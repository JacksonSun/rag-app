#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..init_db import Base
from .mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    token_id = Column(String, unique=True, index=True)
    bg = Column(String)
    bu = Column(String)
    job_grade = Column(String)

    feedback = relationship("Feedback", back_populates="user")

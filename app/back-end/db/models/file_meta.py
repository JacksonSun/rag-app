#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship

from ..init_db import Base
from .mixins import TimestampMixin


class File(TimestampMixin, Base):
    __tablename__ = "file_meta"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    blob_name = Column(String, unique=True, index=True)  # a uuid.[ext] string
    uuid = Column(String, unique=True, index=True)  # a uuid string
    url = Column(String, unique=True, index=True)
    summary = Column(JSON)
    user_id = Column(Integer)

    feedback = relationship("Feedback", back_populates="file")

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ARRAY

from .mixins import TimestampMixin
from ..init_db import Base


class History(TimestampMixin, Base):
    __tablename__ = "qa_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String, index=True)
    source = Column(ARRAY(Integer))
    user_id = Column(Integer)

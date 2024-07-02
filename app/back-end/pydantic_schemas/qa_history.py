#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from pydantic import BaseModel
from datetime import datetime


class HistoryBase(BaseModel):
    question: str
    answer: str
    source: list
    user_id: int

    class Config:
        from_attributes = True


class HistoryCreate(HistoryBase):
    pass


class History(HistoryBase):
    id: int
    create_time: datetime
    last_modified: datetime

    class Config:
        from_attributes = True
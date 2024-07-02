#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from pydantic import BaseModel
from datetime import datetime


class FeedbackBase(BaseModel):
    query: str
    irrelevant_source: str
    user_id: int

    class Config:
        from_attributes = True


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    like_: bool
    create_time: datetime
    last_modified: datetime

    class Config:
        from_attributes = True


class FeedBackES(BaseModel):
    id: int
    user_id: str
    query: str
    irrelevant_source: str
    user_id: int

    # mixin
    create_time: int
    last_modified: int

#!/usr/bin/env python

# -*- encoding: utf-8 -*-
from datetime import datetime

from typing import Optional


from pydantic import BaseModel


# User


class UserBase(BaseModel):
    username: str
    email: str

    token_id: Optional[str] = None

    bg: Optional[str] = None

    bu: Optional[str] = None

    job_grade: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: int

    class Config:
        from_attributes = True


class User(UserBase):
    id: int

    create_time: datetime

    last_modified: datetime

    class Config:
        from_attributes = True

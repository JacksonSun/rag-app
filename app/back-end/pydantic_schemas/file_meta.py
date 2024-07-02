#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pydantic import BaseModel


# File
class FileBase(BaseModel):
    filename: str
    blob_name: str
    uuid: str
    url: str
    summary: str
    user_id: int

    class Config:
        from_attributes = True


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int

    class Config:
        from_attributes = True

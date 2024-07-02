#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from pydantic import BaseModel
from typing import List, Optional


class Document(BaseModel):
    uuid: Optional[str] = None
    chunk_id: Optional[str] = None
    content: Optional[str] = None
    embedding: Optional[List[float]] = None
    filename: Optional[str] = None
    contact_person: Optional[str] = None
    blob_url: Optional[str] = None
    BU: Optional[str] = None
    summary: Optional[str] = None

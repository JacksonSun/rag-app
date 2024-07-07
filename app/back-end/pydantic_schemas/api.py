from typing import List, Optional

from fastapi import Form, UploadFile
from pydantic import BaseModel

from .document import Document, DocumentMetadataFilter, Query, QueryResult


class UpsertRequest(BaseModel):
    documents: List[Document]


class UpsertResponse(BaseModel):
    ids: List[str]


class QueryRequest(BaseModel):
    queries: List[Query]


class QueryResponse(BaseModel):
    results: List[QueryResult]


class DeleteRequest(BaseModel):
    ids: Optional[List[str]] = None
    filter: Optional[DocumentMetadataFilter] = None
    delete_all: Optional[bool] = False


class DeleteResponse(BaseModel):
    success: bool


class SearchPara(BaseModel):
    query: str


class GenerateQaPara(BaseModel):
    file_path: str


class VectorPara(BaseModel):
    file_path: str


class SaveTmpFilePara(BaseModel):
    # f: UploadFile  # TODO
    file: UploadFile = Form(...)


class GenerateSummaryPara(BaseModel):
    tmp_blob_name: str  # TODO


class UploadFilePara(BaseModel):
    tmp_blob_name: str  # TODO
    summary: str


class DocSummaryPara(BaseModel):
    content: str


class ExternalWebpageSummaryPara(BaseModel):
    query: str
    url: str

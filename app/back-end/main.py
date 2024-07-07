#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import io
import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional

import fitz
import pypdf
import requests
from api.search import (
    generate_summary,
    get_relevant_doc,
    get_summary,
    search_external_source,
)
from config import INIT_DB

# from pydantic_schemas.user import UserCreate, UserUpdate
# from pydantic_schemas.feedback import FeedbackCreate
from datastore.factory import get_datastore

# from api.feedback import create_a_feedback
from error import ParameterException, Success
from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain.document_loaders import WebBaseLoader
from loguru import logger
from pydantic_schemas.api import (
    ExternalWebpageSummaryPara,
    SearchPara,
    UpsertRequest,
    UpsertResponse,
)
from pydantic_schemas.document import Document, DocumentMetadata, Source
from services.file import extract_text_from_filepath, get_document_from_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: for now 20230822
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Hello, RAG!"


# @app.post("/summary/")
# async def get_result_summary(sp: SearchPara):
#     if not sp.query:
#         return ParameterException
#     generator = await get_summary(sp.query, datastore)
#     return StreamingResponse(generator, media_type="text/event-stream")


# @app.post("/get_relevant/")
# async def get_relevant_list(sp: SearchPara):
#     if not sp.query:
#         return ParameterException
#     try:
#         res = await get_relevant_doc(sp.query, datastore)
#         relevant_docs, code = res
#         if code == Success.http_status_code:
#             Success.result = relevant_docs
#         return JSONResponse(content=relevant_docs)
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Internal Service Error")


# @app.post("/save-tmp-file/")
# # async def save_tmp_file(stfp: SaveTmpFilePara):
# async def save_tmp_file(file: UploadFile = Form(...)):
#     if not file:
#         return ParameterException
#     res = {"status_code": 200, "tmp_blob_name": store_tmp_file(file)}
#     return JSONResponse(content=res)


# @app.post("/upload_file/")
# async def upload_file(ufp: UploadFilePara):
#     if not ufp.tmp_blob_name or not ufp.summary:
#         return ParameterException
#     try:
#         msg = upload_file_and_meta(ufp.tmp_blob_name, ufp.summary)
#         res = {"status_code": 200, "message": msg}
#         return JSONResponse(content=res)
#     except Exception as e:
#         # TODO: error handling
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post(
#     "/store-file",
# )
# async def store_file(
#     file: UploadFile = File(...)
# ):
#     """
#     Store the uploaded file to the local directory.

#     Args:
#         file (UploadFile): The file to be stored.

#     Returns:
#         JSONResponse: A JSON response containing the filename of the stored file.

#     Raises:
#         HTTPException: If there is an error storing the file.
#     """
#     try:
#         # Get the current working directory
#         cwd = os.getcwd()

#         # Create a new directory for the files if it doesn't exist
#         if not os.path.exists("data"):
#             os.mkdir("data")

#         # Write the file to the local directory
#         with open(os.path.join(cwd, "data", file.filename), "wb") as f:
#             f.write(await file.read())

#         res = {"filename": file.filename}
#         return JSONResponse(content=res)

#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail=f"str({e})")


# @app.post(
#     "/upsert-file",
#     response_model=UpsertResponse,
# )
# async def upsert_file(
#     file: UploadFile = File(...),
#     metadata: Optional[str] = Form(None),
# ):
#     try:
#         metadata_obj = (
#             DocumentMetadata.parse_raw(metadata)
#             if metadata
#             else DocumentMetadata(source=Source.file)
#         )
#         ## if medata_obj do not have document_id, assign file_name as document_id

#     except:
#         metadata_obj = DocumentMetadata(source=Source.file)

#     metadata_obj.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     document = await get_document_from_file(file, metadata_obj)

#     try:
#         ids = await datastore.upsert([document])
#         response = datastore.client.index(
#             index="file-metadata", body=metadata_obj.dict()
#         )

#         # cwd = os.getcwd()
#         # path = os.path.join(cwd, "..", "front-end", "public", "data", file.filename)
#         # TODO: not best practice. Would go wrong if front-end and back-end are deployed on different container
#         path = "../front-end/public/data/" + file.filename

#         # Create a new directory for the files if it doesn't exist
#         # if os.path.exists(path):
#         # os.mkdir("data")

#         # Write the file to the front-end public directory
#         with open(path, "wb") as f:
#             await file.seek(0)
#             f.write(await file.read())

#         return UpsertResponse(ids=ids), {
#             "detail": "File metadata inserted",
#             "id": response["_id"],
#         }
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail=f"str({e})")


# @app.post("/upsert", response_model=UpsertResponse)
# async def upsert(request: UpsertRequest = Body(...)):
#     try:
#         ids = await datastore.upsert(request.documents)
#         return UpsertResponse(ids=ids)
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.get("/get_file_list/")
# async def get_file_list():
#     response = datastore.client.search(
#         index="file-metadata", body={"query": {"match_all": {}}}
#     )
#     return {"file_list": [hit["_source"] for hit in response["hits"]["hits"]]}


# # @app.get("/get_file_list/")
# # async def get_file_list(user_id: int):
# #     res = {"status_code": 200, "response": get_file_list_by_user(user_id)}
# #     return JSONResponse(content=res)
# #     # TODO: error handling


# @app.post(
#     "/generate_file_summary/",
#     description="Generate summary for uploaded file with GenAI",
# )
# async def generate_file_summary(
#     file: UploadFile = File(...),
# ):
#     temp_file = tempfile.NamedTemporaryFile()
#     temp_file.write(await file.read())

#     pages = fitz.open(temp_file.name)
#     text = ""
#     for page in pages:
#         text += page.get_text("all", sort=True)
#     generator = generate_summary(text)
#     return StreamingResponse(generator, media_type="text/event-stream")


# @app.post("/search_external/")
# async def get_external_search_results(sp: SearchPara):
#     if not sp.query:
#         return ParameterException
#     res, code = search_external_source(sp.query, num=10)
#     if code == Success.http_status_code:
#         Success.result = res
#     return JSONResponse(content=res)


# @app.post("/webpage_summary/")
# def get_external_webpage_summary(ewp: ExternalWebpageSummaryPara):
#     if not ewp.url or not ewp.query:
#         return ParameterException
#     try:
#         response = requests.get(ewp.url)
#         pdf_file = io.BytesIO(response.content)
#         pdf_reader = pypdf.PdfReader(pdf_file)
#         text = pdf_reader.pages[0].extract_text() + pdf_reader.pages[1].extract_text()
#     except Exception:
#         loader = WebBaseLoader(ewp.url)
#         content = loader.load()
#         if len(content) > 0:
#             text = content[0].page_content
#     generator = generate_summary(text)
#     return StreamingResponse(generator, media_type="text/event-stream")


# # @app.post("/user/")
# # async def upsert_user(request: Union[UserUpdate, UserCreate]):
# #     """
# #     Upserts a user in the database.

# #     Args:
# #         request (UserBase): The user object to be upserted.

# #     Returns:
# #         JSONResponse: A JSON response containing the status code and message.
# #     Raises:
# #         HTTPException: If there is an error upserting the user.
# #     """
# #     try:
# #         ret = update_or_create_user(request)
# #         res = {"status_code": 200, "response": ret}
# #         return JSONResponse(content=res)
# #     except Exception as e:
# #         # TODO: error handling
# #         raise HTTPException(status_code=400, detail=str(e))


# # @app.post("/feedback/")
# # async def create_feedback(request: FeedbackCreate):
# #     """
# #     Create a feedback in the database.

# #     Args:
# #         request (Feedback): The feedback object to be created.

# #     Returns:
# #         JSONResponse: A JSON response containing the status code and message.
# #     Raises:
# #         HTTPException: If there is an error creating the feedback.
# #     """
# #     try:
# #         ret = create_a_feedback(request)
# #         res = {"status_code": 200, "response": ret}
# #         return JSONResponse(content=res)
# #     except Exception as e:
# #         # TODO: error handling
# #         raise HTTPException(status_code=400, detail=str(e))


# @app.on_event("startup")
# async def startup():
#     """
#     Initializes the global datastore variable when api startup.
#     """
#     global datastore
#     datastore = await get_datastore()
#     if INIT_DB:
#         await init_data("../../data/")


# # only for development
# async def init_data(filepath: str):
#     # clean up db
#     await datastore.delete(delete_all=True)
#     datastore.client.indices.delete(index="file-metadata", ignore=[404, 400])
#     shutil.rmtree("../front-end/public/data", ignore_errors=True)
#     # make sure the directory exists
#     if not os.path.exists("../front-end/public/data"):
#         os.makedirs("../front-end/public/data")
#     # init_data
#     files = os.listdir(filepath)
#     docs = []
#     for i, file in enumerate(files):
#         document_metadata = {
#             "source_id": "folder" + str(i),
#             # "source_id": "test:" + file,
#             "source": "file",
#             "url": f"data/{file}",
#             "author": "author_" + str(i),
#             "title": file,
#         }
#         file_meta = {
#             **document_metadata,
#             "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "summary": """EMI, or Equated Monthly Installment, is a fixed payment amount made by a borrower to a lender at a specified date each calendar month.
#             EMI payments include both principal and interest repayment. The sum of principal and interest is divided by the loan tenure, consisting of several months.
#             This division ensures a consistent monthly payment, simplifying budgeting for the borrower.""",
#         }
#         datastore.client.index(index="file-metadata", body=file_meta)
#         shutil.copy(os.path.join(filepath, file), f"../front-end/public/data/{file}")
#         extracted_text = extract_text_from_filepath(os.path.join(filepath, file))
#         doc = Document(text=extracted_text, metadata=document_metadata)
#         docs.append(doc)

#     await datastore.upsert(docs)

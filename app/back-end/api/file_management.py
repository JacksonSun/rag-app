#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import asyncio
import uuid
from datetime import datetime
from fastapi import UploadFile
from typing import AsyncIterable
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.chat_models import AzureChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

from .prompting import UPLOAD_DOCUMENT_SUMMARY_PROMPT_TEMPLATE
from config import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    OPENAI_API_TYPE,
    OPENAI_API_VERSION,
    BLOB_CONTAINER_NAME_TMP,
    BLOB_CONTAINER_NAME,
    BLOB_SERVICE_CONNECT_STR,
)

from .utils import (
    get_postgre_conn,
    clean_db_response,
    get_contact_person_from_filename,
    get_kafka_producer,
    convert_datetime_to_str,
)
from crud.file_meta_crud import get_files, create_new_file
from pydantic_schemas.file_meta import FileCreate
from api.blob import Blob
from fastapi.encoders import jsonable_encoder


VALID_CONTENT_TYPES = [
    "application/pdf",  # .pdf
    "application/vnd.ms-powerpoint",  # .ppt
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
]


BLOB_DIR_NAME = (
    "uploaded_lesson_learned/"  # TODO:20230905 - for testing. need to be changed
)


MIN_SIMILARITY = 0.18
DEFAULT_MODEL = "gpt-35-turbo-0301"
DEFAULT_TEMPERATURE = 0
MAX_TOKENS = 1000


def _get_streaming_llm(deployment, temperature, max_tokens):
    temperature = min(temperature, 1) if temperature > 1 else max(temperature, 0)
    max_tokens = min(max_tokens, 1000) if max_tokens > 1000 else max(max_tokens, 0)
    callback = AsyncIteratorCallbackHandler()
    llm = AzureChatOpenAI(
        deployment_name=deployment,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_base=OPENAI_API_BASE,
        openai_api_type=OPENAI_API_TYPE,
        openai_api_key=OPENAI_API_KEY,
        openai_api_version=OPENAI_API_VERSION,
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )
    return llm, callback


def store_tmp_file(file: UploadFile, language: str = "CN") -> str:
    """store_tmp_file: Store file into blob tmp container and return blob name

    Args:
        file (UploadFile): file to be stored
        language (str, optional): language of the file. Defaults to "CN". #TODO: default language, enum languages

    Returns:
        str: blob name of the stored file
    """
    # 0. validation on file content type
    if file.content_type not in VALID_CONTENT_TYPES:
        return "error"  # TODO
    # 1. save file into blob tmp container - return blob name
    # filename = year/month/date/uuid
    blob = Blob(connection_string=BLOB_SERVICE_CONNECT_STR)
    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    new_uuid = str(uuid.uuid4())
    ext = "." + file.filename.split(".")[-1]
    # set metadata
    metadata = blob.form_metadata(
        uuid=new_uuid,
        filename=file.filename,
        contact_person=get_contact_person_from_filename(file.filename),
        language=language,
    )
    # upload blob
    blob_name = blob.blob_upload(
        blob_name=date_str + "/" + new_uuid + ext,
        container_name=BLOB_CONTAINER_NAME_TMP,
        metadata=metadata,
        file=file,
    )
    # 2. return blob_name
    return blob_name
    # TODO: error handling


async def get_document_summary(
    blob_name: str,
    deployment=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=MAX_TOKENS,
) -> AsyncIterable[str]:
    """get_document_summary: Given a blob name, generate summary of the file stored in Azure Blob Storage

    Args:
        blob_name (str): blob name of the file to be summarized
        deployment (_type_, optional): model of llm to be used . Defaults to DEFAULT_MODEL.
        temperature (_type_, optional): temperature of llm. Defaults to DEFAULT_TEMPERATURE.
        max_tokens (_type_, optional): maximum amount of token for llm. Defaults to MAX_TOKENS.

    Returns:
        AsyncIterable[str]: generator of summary

    """
    blob = Blob(connection_string=BLOB_SERVICE_CONNECT_STR)
    content = blob.load_blob(
        container_name=BLOB_CONTAINER_NAME_TMP, blob_name=blob_name
    )

    # TODO all file return list? with page_content
    content = content[0].page_content

    llm, callback = _get_streaming_llm(deployment, temperature, max_tokens)
    summary_template = ChatPromptTemplate.from_messages(
        [
            HumanMessagePromptTemplate.from_template(
                UPLOAD_DOCUMENT_SUMMARY_PROMPT_TEMPLATE
            )
        ]
    )
    task = asyncio.create_task(
        llm.agenerate(
            [
                summary_template.format_messages(input_text=content),
            ]
        )
    )
    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        # TODO: error handling
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()
    await task


def upload_file_and_meta(tmp_blob_name: str, summary: str):
    """upload_file_and_db: Upload file to Azure Blob Storage and insert metadata into Postgres DB (FILE_METADATA table)

    Args:
        tmp_blob_name (str): blob name of the file to be uploaded in tmp container
        summary (str): summary of the file

    Returns:
        str: ok message
    """

    try:
        blob = Blob(connection_string=BLOB_SERVICE_CONNECT_STR)
        # 1. copy file from tmp container to actual container
        uuid_filename = tmp_blob_name.split("/")[-1]
        blob_url, filename = blob.copy_blob_in_azure(
            src_container_name=BLOB_CONTAINER_NAME_TMP,
            src_blob_name=tmp_blob_name,
            dest_container_name=BLOB_CONTAINER_NAME,
            dest_blob_name=BLOB_DIR_NAME + uuid_filename,
        )
        # 2. insert blob url, summary into FILE_METADATA table
        # TODO: insert blob_url, summary, file id, other file meta into ES
        try:
            file_meta = FileCreate(
                filename=filename,
                url=blob_url,
                summary=summary,
                user_id=0,  # TODO: change it to user_id
                blob_name=uuid_filename,
                uuid=uuid_filename.split(".")[0],
            )
            db_session = get_postgre_conn()
            file_created = create_new_file(db_session, file_meta)
        except Exception as e:
            # TODO: error handling
            # revert to delete blob
            blob.delete_blob(
                container_name=BLOB_CONTAINER_NAME,
                blob_name=BLOB_DIR_NAME + uuid_filename,
            )
            raise e

        try:
            # Kafka producer to trigger data pipeline
            producer = get_kafka_producer()
            producer.send("rd_expert_pipeline", value={"blob_name": blob_url})
            producer.flush()
        except Exception as e:
            # revert db
            db_session.rollback()
            raise e

        # final return
        db_session.commit()
        db_session.close()
        return convert_datetime_to_str(jsonable_encoder(file_created))
    except Exception as e:
        raise e


def get_file_list_by_user(user_id: int):
    """get_file_list_by_user: Get list of files uploaded by user

    Args:
        user_id (int): user_id in FILE_METADATA table

    Returns:
        dict[]: list of dict that contains files uploaded by user
    """
    # TODO: error handling
    db_session = get_postgre_conn()
    files = get_files(db_session, user_id)
    files = [clean_db_response(f.__dict__) for f in files]
    return files

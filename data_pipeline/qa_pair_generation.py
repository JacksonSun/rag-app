#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import re
import json
import traceback
import pandas as pd
from typing import List
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import AzureChatOpenAI
from langchain.output_parsers import (
    StructuredOutputParser,
    ResponseSchema,
)
from langchain.document_loaders import PyPDFLoader
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from config import (
    OPENAI_API_KEY,
    OPENAI_DEPLOYMENT_ENDPOINT,
    OPENAI_API_TYPE,
    OPENAI_DEPLOYMENT_VERSION,
    BLOB_CONN_STRING,
    GENERATE_QA_PAIR_PROMPT_TEMPLATE,
)

DEFAULT_MODEL = "gpt-35-turbo-0301"
DEFAULT_TEMPERATURE = 0
MAX_TOKENS = 1000


def _generate_qa_pair(content):
    response_schemas = [
        ResponseSchema(
            name="question", description="A question generated from input text snippet."
        ),
        ResponseSchema(name="answer", description="Proposed answer for the question."),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(GENERATE_QA_PAIR_PROMPT_TEMPLATE)
        ],
        input_variables=["user_prompt"],
        partial_variables={"format_instructions": format_instructions},
    )
    try:
        llm = AzureChatOpenAI(
            deployment_name=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            openai_api_base=OPENAI_DEPLOYMENT_ENDPOINT,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_key=OPENAI_API_KEY,
            openai_api_version=OPENAI_DEPLOYMENT_VERSION,
        )
        user_query = prompt.format_prompt(user_prompt=content)
        user_query_output = llm(user_query.to_messages())
        json_string = re.search(
            r"```json\n(.*?)```", user_query_output.content, re.DOTALL
        ).group(1)
        qa_pair_list = json.loads(f"[{json_string}]")
        return qa_pair_list
    except Exception as e:
        print(e)
        return []


def _get_blob_connection(connection_string: str) -> BlobServiceClient:
    try:
        return BlobServiceClient.from_connection_string(connection_string)
    except Exception as e:
        raise traceback.format_exc(e)


def _get_blob_list(
    service_client: BlobServiceClient, container_name: str, sub_container_name: str = ""
) -> List:
    try:
        container_client = service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(name_starts_with=sub_container_name)
        return [blob["name"] for blob in blob_list]
    except Exception as e:
        raise traceback.format_exc(e)


def _download_blob(
    connection_string: str,
    container_name: str,
    blob_name: str,
    container_path: str = "",
    local_filename: str = None,
    local_path: str = "",
) -> None:
    try:
        blob = BlobClient.from_connection_string(
            conn_str=connection_string,
            container_name=container_name,
            blob_name=os.path.join(container_path, blob_name),
        )
        if local_filename == None:
            local_filename = blob_name
            path = os.path.join(local_path, local_filename)
            with open(path, "wb") as download_file:
                stream = blob.download_blob()
                data = stream.readall()
                download_file.write(data)
            return None
    except ResourceNotFoundError:
        raise ResourceNotFoundError("The specified blob does not exist.")
    except Exception as e:
        raise traceback.format_exc(e)


def _get_file_content(file_path: str):
    try:
        if file_path.lower().endswith(".pdf"):
            content = ""
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            for page in pages:
                content += page.page_content
            return content
            # loader = UnstructuredPDFLoader(file_path)
            # content = loader.load()
            # return content[0].page_content
    except Exception as e:
        print("Get file content failed.", e)
        return None


def generate_qa_pair_pipeline(local_path: str):
    sc = _get_blob_connection(BLOB_CONN_STRING)
    blob_list = _get_blob_list(
        service_client=sc,
        container_name="rd-expert",
        sub_container_name="Lesson Learned Material",
    )
    df = pd.DataFrame(columns=["question", "answer", "source"])
    for blob_name in blob_list:
        _download_blob(
            connection_string=BLOB_CONN_STRING,
            container_name="rd-expert",
            blob_name=blob_name,
            container_path="",
            local_filename=None,
            local_path=local_path,
        )
        content = _get_file_content(local_path + blob_name)
        if content:
            qa_pair_list = _generate_qa_pair(content)
            for p in qa_pair_list:
                p["source"] = blob_name
                df.loc[len(df)] = p
    df.to_csv(local_path + "qa_pair.csv")

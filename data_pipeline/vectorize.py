#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.document_loaders import (
    UnstructuredPDFLoader,
)

from .utils import combine_duplicate_docs, get_redis_conn, data_clean, base_response
from .config import (
    OPENAI_API_KEY,
    OPENAI_DEPLOYMENT_ENDPOINT,
    OPENAI_API_TYPE,
    OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
    OPENAI_ENDPOINT_4K,
    REDIS_URL,
    REDIS_INDEX,
)
import yaml
import fitz
import tempfile
import os
import numpy as np
import json
import requests

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File


def _classifier(pdf_file: str):
    with open(pdf_file, "rb") as f:
        pdf = fitz.open(f)
        res = True
        for page in pdf:
            image_area = 0.0
            text_area = 0.0
            for b in page.get_text("blocks"):
                if "<image:" in b[4]:
                    r = fitz.Rect(b[:4])
                    image_area = image_area + abs(r)
                else:
                    r = fitz.Rect(b[:4])
                    text_area = text_area + abs(r)
            if image_area == 0.0 and text_area != 0.0:
                res = True
            if text_area == 0.0 and image_area != 0.0:
                res = False
        return res


def _pdf_loader(file_path: str):
    if file_path.lower().endswith(".pdf"):
        if _classifier(file_path):
            loader = UnstructuredPDFLoader(file_path)
            return loader.load()
        else:
            return None
    return None


def search_vector(query):
    embedding_model = OpenAIEmbeddings(
        deployment=OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
        openai_api_base=OPENAI_DEPLOYMENT_ENDPOINT,
        openai_api_type=OPENAI_API_TYPE,
        openai_api_key=OPENAI_API_KEY,
    )
    rds = Redis.from_existing_index(
        embedding_model, redis_url=REDIS_URL, index_name=REDIS_INDEX
    )
    results = combine_duplicate_docs(rds.similarity_search_with_score(query, k=10))
    return results


def insert_vector(file_path: str, uid: str):
    file_path = "/sites/RDExpert" + file_path
    file_path = file_path.replace("'", "%27%27")

    redis_conn = get_redis_conn()
    with open("/app/credential.yml", "r") as f:
        conn_config = yaml.safe_load(f)
    url = "https://liteon.sharepoint.com/sites/RDExpert"
    ctx = ClientContext(url).with_client_certificate(**conn_config["cert_settings"])
    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = temp_dir + "/" + file_path
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as output_file:
            response = File.open_binary(ctx, file_path)
            output_file.write(response.content)
        doc = _pdf_loader(local_path)
        if doc is not None:
            embed_model = OpenAIEmbeddings(
                deployment=OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
                openai_api_base=OPENAI_DEPLOYMENT_ENDPOINT,
                openai_api_type=OPENAI_API_TYPE,
                openai_api_key=OPENAI_API_KEY,
                chunk_size=1,
            )
            content = ""
            for d in doc:
                content += d.page_content
            texts = [data_clean(content)]
            metadatas = [doc[0].metadata]
            r = requests.post(
                url=OPENAI_ENDPOINT_4K,
                json={
                    "messages": [
                        {
                            "role": "assistant",
                            "content": f"""
                        Write a concise and comprehensive summary of the input text.
                        Summary should include all details and no longer than 1000 words.
                        DON NOT have person name in summary.
                        Have CONTEXT, PROBLEM, SOLUTION, and RESULT in summary.
                        INPUT TEXT: {data_clean(content)}
                        """,
                        }
                    ],
                    "temperature": 0,
                    "max_tokens": 2000,
                    "top_p": 0.95,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "stop": "None",
                },
                headers={"API-KEY": OPENAI_API_KEY},
            )

            summary = ""
            if "content" in json.loads(r.text)["choices"][0]["message"].keys():
                summary = json.loads(r.text)["choices"][0]["message"]["content"]

            ids = []

            embedding = embed_model.embed_documents(texts)
            embedding_summary = embed_model.embed_documents([summary])

            pipeline = redis_conn.pipeline(transaction=False)
            for i, text in enumerate(texts):
                key = f"rdexpert:autoflow:{uid}-{i}"
                key_summary = f"rdexpert:autoflowsummary:{uid}-{i}"
                metadata = metadatas[i] if metadatas else {}
                embeddings = embedding[i]
                pipeline.hset(
                    key,
                    mapping={
                        "content": text,
                        "content_vector": np.array(
                            embeddings, dtype=np.float32
                        ).tobytes(),
                        "metadata": json.dumps(metadata),
                    },
                )
                pipeline.hset(
                    key_summary,
                    mapping={
                        "content": summary,
                        "content_vector": np.array(
                            embedding_summary, dtype=np.float32
                        ).tobytes(),
                        "metadata": json.dumps(metadata),
                    },
                )
                ids.append(key)

                # Write batch
                if i % 1000 == 0:
                    pipeline.execute()

            # Cleanup final batch
            pipeline.execute()
            return base_response("OK")
        return base_response("No vector is inserted")

#!/usr/bin/env python
# -*- encoding: utf-8 -*-


# OpenAI
OPENAI_API_KEY = ""
OPENAI_API_BASE = "https://prd-gpt-scus.openai.azure.com"
OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo-0301"
OPENAI_API_VERSION = "2023-05-15"
OPENAI_API_TYPE = "azure"
OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-ada-002"
OPENAI_MODEL_LIST = ["gpt-35-turbo", "gpt-4", "gpt-4-32k", "gpt-35-turbo-0301"]
OPENAI_ENDPOINT_4K = "https://prd-gpt-scus.openai.azure.com/openai/deployments/gpt-4-8k-0314/chat/completions?api-version=2023-03-15-preview"

# Azure Blob
BLOB_CONN_STRING = ""
BLOB_CONTAINER_NAME = ""
BLOB_SERVICE_CONNECT_STR = ""

KAFKA_CONNECT_URL = ""
KAFKA_TOPIC = ""

ELASTICSEARCH_CLOUD_ID = ""
ELASTICSEARCH_API_KEY = ""
ELASTICSEARCH_INDEX_NAME = ""

POSTGRE_CONNECT_URL = (
    "postgresql+psycopg2://postgres:liteonpostgres@10.1.14.89:5432/postgres"
)

DEFAULT_CHUNK_SIZE = 2000
MIN_CHUNK_SIZE_CHARS = 500
MIN_LINE_CHARS = 7
EMBEDDINGS_BATCH_SIZE = 10
PAGE_SPLITTER = "###PAGE_SPLITTER###"

BU_CIPS = "CIPS"

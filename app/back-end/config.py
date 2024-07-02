#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os

# DEV CONFIG
INIT_DB = False


# OPENAI


# Azure OpenAI


# Azure Translate API
# TRANSLATE_KEY = "cdec702cbd1b4057922c9023e6249270"
# TRANSLATE_EP = "https://api.cognitive.microsofttranslator.com/"
# TRANSLATE_LOCATION = "eastasia"
# TRANSLATE_PATH = "/translate"

# Auzre URL
# SCREENSHOT_URL_BASE =
# DOCUMENT_URL_BASE =
# BLOB_URL_BASE =

# Azure Blob
# BLOB_CONTAINER_NAME_TMP =
# BLOB_CONTAINER_NAME =
# BLOB_SERVICE_CONNECT_STR =


# Postgre
POSTGRE_HOST = "localhost"
POSTGRE_PORT = 5432
POSTGRE_USERNAME = ""
POSTGRE_PASSWORD = ""


# Datastore
DATASTORE = "elasticsearch"

########   Elasticsearch #########
ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")


ELASTICSEARCH_CLOUD_ID = ""
ELASTICSEARCH_USERNAME = ""
ELASTICSEARCH_PASSWORD = ""
ELASTICSEARCH_API_KEY = ""

ELASTICSEARCH_INDEX = "mck_rag"
ELASTICSEARCH_REPLICAS = 1
ELASTICSEARCH_SHARDS = 1

## Search parameters for ES
SEARCH_TYPE = "hybrid"  # choose one from [hybrid, keyword, semantic]
SIZE = 5  # number of results to return
K = 5  # number of candidates to return from semantic search
NUM_CANDIDATES = 50  # The number of nearest neighbor candidates to consider per shard. Cannot exceed 10,000. Elasticsearch collects num_candidates results from each shard, then merges them to find the top k results. Increasing num_candidates tends to improve the accuracy of the final k results.
WINDOW_SIZE = 100  # the size of the individual result sets per query, higher the better
########## Elasticsearch ##########


# Google search API
GOOGLE_API_KEY = "AIzaSyBkylbPbc8XfFZsNjTQgxGcxcJauojMHJE"
GOOGLE_CSE_ID = "c1bd40c67063e4a1d"

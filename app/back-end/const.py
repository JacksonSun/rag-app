#!/usr/bin/env python
# -*- encoding: utf-8 -*-


MIN_SIMILARITY = 0.18  # The threshold of similarity score to retrieve a document
RESPONSE_MODEL = "gpt-4-8k-0314"  # The default model to use for generating response
RESPONSE_TEMPERATURE = 0.1  # The default temperature to use for generating response
MAX_TOKENS = 1024
FILE_SUMMARY_MODEL = "gpt-35-turbo-0301"
FILE_SUMMARY_MODEL_TEMPERATURE = 0.3
FILE_SUMMARY_CHARATER_LIMIT = 2000
K = 4  # The number of documents return to the user

# Chunking strategy
# Each chunk will be less than CHUNK_SIZE tokens, but at least MIN_CHUNK_SIZE_CHARS characters
CHUNK_SIZE = 500  # The target size of each text chunk in tokens
MIN_CHUNK_SIZE_CHARS = 350  # The minimum size of each text chunk in characters
MIN_CHUNK_LENGTH_TO_EMBED = (
    7  # The minimum number of characters a line must have to be kept
)
EMBEDDINGS_BATCH_SIZE = 10  # The number of chunks to embed at once
PAGE_SPLITTER = "###PAGE_SPLITTER###"  # The string to use to split pages
MAX_NUM_CHUNKS = 10000  # The maximum number of chunks to generate from a text
MIN_LINE_CHARS = 10
SPECIAL_CHARS = "!@�§€�"

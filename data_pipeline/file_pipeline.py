#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import os
import tempfile
import psycopg2
import urllib.parse
import tiktoken
import json
import uuid
import openai
import pypdf
from typing import List, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_random_exponential
from azure.storage.blob import BlobServiceClient
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from langchain.document_loaders import (
    TextLoader,
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)

from document import Document
from config import (
    BLOB_CONTAINER_NAME,
    BLOB_SERVICE_CONNECT_STR,
    KAFKA_CONNECT_URL,
    KAFKA_TOPIC,
    ELASTICSEARCH_CLOUD_ID,
    ELASTICSEARCH_API_KEY,
    ELASTICSEARCH_INDEX_NAME,
    POSTGRE_CONNECT_URL,
    DEFAULT_CHUNK_SIZE,
    MIN_CHUNK_SIZE_CHARS,
    MIN_LINE_CHARS,
    PAGE_SPLITTER,
    EMBEDDINGS_BATCH_SIZE,
    OPENAI_API_BASE,
    OPENAI_API_VERSION,
    OPENAI_API_KEY,
    OPENAI_API_TYPE,
    OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
    BU_CIPS,
)

openai.api_base = OPENAI_API_BASE
openai.api_version = OPENAI_API_VERSION
openai.api_key = OPENAI_API_KEY
openai.api_type = OPENAI_API_TYPE


class FileIngestionPipeline:
    def __init__(self, blob_name, bu_name):
        self.bu_name = bu_name
        self.blob_name = blob_name
        self.service_client = BlobServiceClient.from_connection_string(
            BLOB_SERVICE_CONNECT_STR
        )
        self.container_client = self.service_client.get_container_client(
            BLOB_CONTAINER_NAME
        )
        self.es_client = self.get_es_conn(
            cloud_id=ELASTICSEARCH_CLOUD_ID, api_key=ELASTICSEARCH_API_KEY
        )
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def get_es_conn(
        self,
        elasticsearch_url=None,
        cloud_id=None,
        api_key=None,
        username=None,
        password=None,
    ):
        # Check if both elasticsearch_url and cloud_id are defined
        if elasticsearch_url and cloud_id:
            raise ValueError(
                "Both elasticsearch_url and cloud_id are defined. Please provide only one."
            )
        # Initialize connection parameters dictionary
        connection_params = {}
        # Define the connection based on the provided parameters
        if elasticsearch_url:
            connection_params["hosts"] = [elasticsearch_url]
        elif cloud_id:
            connection_params["cloud_id"] = cloud_id
        else:
            raise ValueError("Please provide either elasticsearch_url or cloud_id.")
        # Add authentication details based on the provided parameters
        if api_key:
            connection_params["api_key"] = api_key
        elif username and password:
            connection_params["basic_auth"] = (username, password)
        else:
            pass
        # Establish the Elasticsearch client connection
        es_client = Elasticsearch(**connection_params)
        try:
            es_client.info()
        except Exception as e:
            raise e
        return es_client

    def __remove_lines(self, text: str, min_chars: int = 10) -> str:
        def is_valid_line(line):
            return len(line) >= min_chars

        lines = text.split("\n")
        lines = [line for line in lines if is_valid_line(line)]
        return "\n".join(lines)

    def __clean_data(self, text: str) -> str:
        r = text.replace(PAGE_SPLITTER, "\n")
        r = self.__remove_lines(r, MIN_LINE_CHARS)
        r = r.replace("\n", " ").strip()
        return r

    def index_into_es(self, index_name, doc_dict):
        try:
            res = self.es_client.index(index=index_name, document=doc_dict)
            return res
        except Exception as e:
            print("Elasticsearch index error", e)
            return None

    def get_file_content_from_blob(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        blob_url = blob_client.url
        blob_metadata = blob_client.get_blob_properties().metadata
        doc_content = Document(
            uuid=blob_metadata["uuid"],
            filename=blob_metadata["filename"],
            contact_person=blob_metadata["contact_person"],
            blob_url=blob_url,
            BU=self.bu_name,
        )
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{blob_name}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(f"{file_path}", "wb") as file:
                    blob_data = blob_client.download_blob()
                    blob_data.readinto(file)
                try:
                    if file_path.lower().endswith(".txt"):
                        content = TextLoader(file_path).load()
                        doc_content.content = content[0].page_content
                    elif file_path.lower().endswith(".pdf"):
                        pdf_reader = pypdf.PdfReader(file_path)
                        text = [page.extract_text() for page in pdf_reader.pages]
                        doc_content.content = PAGE_SPLITTER.join(text)
                    elif file_path.lower().endswith(".docx"):
                        content = Docx2txtLoader(file_path).load()
                        doc_content.content = content[0].page_content
                    elif file_path.lower().endswith(".doc"):
                        content = UnstructuredWordDocumentLoader(file_path).load()
                        doc_content.content = content[0].page_content
                    elif file_path.lower().endswith(
                        ".pptx"
                    ) or file_path.lower().endswith(".ppt"):
                        content = UnstructuredPowerPointLoader(file_path).load()
                        doc_content.content = content[0].page_content
                    else:
                        raise Exception("Unsupported file type")
                except Exception as e:
                    raise e
        except Exception as e:
            raise e
        return doc_content

    def get_file_summary_from_postgre(self, file_name: str) -> str:
        result = urllib.parse.urlparse(POSTGRE_CONNECT_URL)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        psy_conn = None
        summary = ""
        try:
            psy_conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port,
            )
        except (Exception, psycopg2.DatabaseError) as e:
            raise e
        if psy_conn:
            cursor = psy_conn.cursor()
            select_query = (
                "SELECT * FROM file_meta WHERE filename = '" + file_name + ".pdf';"
            )
            cursor.execute(select_query)
            file_record = cursor.fetchone()
            if file_record:
                summary = file_record[3]
        return summary

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def get_embeddings(self, texts):
        deployment = OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME
        response = {}
        if deployment == None:
            response = openai.Embedding.create(
                input=texts, model="text-embedding-ada-002"
            )
        else:
            response = openai.Embedding.create(input=texts, deployment_id=deployment)
        data = response["data"]
        return [result["embedding"] for result in data]

    def __get_text_chunks(self, text: str, chunk_token_size: int) -> List[str]:
        if not text or text.isspace():
            return []
        if PAGE_SPLITTER in text:
            SPLITTER = [PAGE_SPLITTER]
        else:
            SPLITTER = [".", "?", "!", "\n", "。", "？", "！"]
        tokens = self.tokenizer.encode(text, disallowed_special=())
        chunks = []
        num_chunks = 0

        while tokens:
            chunk = tokens[:chunk_token_size]
            # Decode the chunk into text
            chunk_text = self.tokenizer.decode(chunk)
            # Skip the chunk if it is empty or whitespace
            if not chunk_text or chunk_text.isspace():
                # Remove the tokens corresponding to the chunk text from the remaining tokens
                tokens = tokens[len(chunk) :]
                # Continue to the next iteration of the loop
                continue

            # Find the last period or punctuation mark in the chunk
            last_punctuation = max(chunk_text.rfind(p) for p in SPLITTER)
            # If there is a punctuation mark, and the last punctuation index is before MIN_CHUNK_SIZE_CHARS
            if last_punctuation != -1 and last_punctuation > MIN_CHUNK_SIZE_CHARS:
                # Truncate the chunk text at the punctuation mark
                chunk_text = chunk_text[: last_punctuation + len(SPLITTER[0])]

            chunk_text_to_append = self.__clean_data(chunk_text)
            if len(chunk_text_to_append) >= MIN_CHUNK_SIZE_CHARS:
                chunks.append(chunk_text_to_append)
            else:
                break
            tokens = tokens[
                len(self.tokenizer.encode(chunk_text, disallowed_special=())) :
            ]
            num_chunks += 1

        # Handle the remaining tokens
        if tokens:
            remaining_text = self.__clean_data(self.tokenizer.decode(tokens))
            if len(remaining_text) > MIN_CHUNK_SIZE_CHARS:
                chunks.append(remaining_text)
            else:
                if len(chunks) > 0:
                    chunks[-1] += remaining_text
                else:
                    chunks.append(remaining_text)
        return chunks

    def create_document_chunks(
        self, doc: Document, chunk_token_size: Optional[int]
    ) -> Tuple[List[Document], str]:
        if not doc.content or doc.content.isspace():
            return [], doc.uuid or str(uuid.uuid4())
        doc_id = doc.uuid or str(uuid.uuid4())
        text_chunks = self.__get_text_chunks(doc.content, chunk_token_size)
        doc_chunks = []
        for i, text_chunk in enumerate(text_chunks):
            doc_chunk = Document(
                uuid=doc.uuid,
                chunk_id=f"{doc_id}_{i}",
                content=text_chunk,
                filename=doc.filename,
                contact_person=doc.contact_person,
                blob_url=doc.blob_url,
                BU=doc.BU,
                summary=doc.summary,
            )
            doc_chunks.append(doc_chunk)
        return doc_chunks, doc_id

    def get_document_vector(
        self, doc: Document, chunk_token_size: int
    ) -> List[Document]:
        doc_chunks, doc_id = self.create_document_chunks(doc, chunk_token_size)
        if not doc_chunks:
            return []

        # Get all the embeddings for the document chunks in batches, using get_embeddings
        embeddings: List[List[float]] = []
        for i in range(0, len(doc_chunks), EMBEDDINGS_BATCH_SIZE):
            # Get the text of the chunks in the current batch
            batch_texts = [
                chunk.content for chunk in doc_chunks[i : i + EMBEDDINGS_BATCH_SIZE]
            ]
            batch_embeddings = self.get_embeddings(batch_texts)
            embeddings.extend(batch_embeddings)

        # Update the document chunk objects with the embeddings
        for i, chunk in enumerate(doc_chunks):
            chunk.embedding = embeddings[i]
        return doc_chunks

    def run_pipeline(self):
        # Get file content from blob
        doc_content = self.get_file_content_from_blob(self.blob_name)

        # Get file summary from postgreSQL
        summary = self.get_file_summary_from_postgre(doc_content.filename)
        doc_content.summary = summary

        # Get file vector
        doc_chunks = self.get_document_vector(doc_content, DEFAULT_CHUNK_SIZE)
        # Index into Elasticsearch
        for chunk in doc_chunks:
            self.index_into_es(ELASTICSEARCH_INDEX_NAME, chunk.model_dump())


def consumer_from_kafka():
    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_CONNECT_URL,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    consumer.subscribe(topics=KAFKA_TOPIC)
    for message in consumer:
        print("%d:%d: v=%s" % (message.partition, message.offset, message.value))
        blob_name = message.value.get("blob_name")
        FileIngestionPipeline(blob_name, BU_CIPS).run_pipeline()


if __name__ == "__main__":
    consumer_from_kafka()

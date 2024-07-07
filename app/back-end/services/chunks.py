import uuid
from typing import Dict, List, Optional, Tuple

import fitz
import tiktoken
from const import (
    CHUNK_SIZE,
    EMBEDDINGS_BATCH_SIZE,
    MAX_NUM_CHUNKS,
    MIN_CHUNK_LENGTH_TO_EMBED,
    MIN_CHUNK_SIZE_CHARS,
    PAGE_SPLITTER,
)
from pydantic_schemas.document import Document, DocumentChunk, DocumentChunkMetadata
from services.openai import get_embeddings

from .preprocess import clean_data

# Global variables
tokenizer = tiktoken.get_encoding(
    "cl100k_base"
)  # The encoding scheme to use for tokenization


def get_text_chunks(text: str, chunk_token_size: Optional[int]) -> List[str]:
    """
    Split a text into chunks of ~CHUNK_SIZE tokens, based on punctuation and newline boundaries.

    Args:
        text: The text to split into chunks.
        chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

    Returns:
        A list of text chunks, each of which is a string of ~CHUNK_SIZE tokens.
    """
    # Return an empty list if the text is empty or whitespace
    if not text or text.isspace():
        return []
    if PAGE_SPLITTER in text:
        SPLITTER = [PAGE_SPLITTER]
    else:
        SPLITTER = [".", "?", "!", "\n", "。", "？", "！"]
    # Tokenize the text
    tokens = tokenizer.encode(text, disallowed_special=())

    # Initialize an empty list of chunks
    chunks = []

    # Use the provided chunk token size or the default one
    chunk_size = chunk_token_size or CHUNK_SIZE

    # Initialize a counter for the number of chunks
    num_chunks = 0

    # Loop until all tokens are consumed
    while tokens and num_chunks < MAX_NUM_CHUNKS:
        # Take the first chunk_size tokens as a chunk
        chunk = tokens[:chunk_size]

        # Decode the chunk into text
        chunk_text = tokenizer.decode(chunk)

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

        # Remove any newline characters and strip any leading or trailing whitespace
        chunk_text_to_append = clean_data(chunk_text)

        if len(chunk_text_to_append) > MIN_CHUNK_LENGTH_TO_EMBED:
            # Append the chunk text to the list of chunks
            chunks.append(chunk_text_to_append)

        # Remove the tokens corresponding to the chunk text from the remaining tokens
        tokens = tokens[len(tokenizer.encode(chunk_text, disallowed_special=())) :]

        # Increment the number of chunks
        num_chunks += 1

    # Handle the remaining tokens
    if tokens:
        remaining_text = clean_data(tokenizer.decode(tokens))
        if len(remaining_text) > MIN_CHUNK_SIZE_CHARS:
            chunks.append(remaining_text)
        else:
            chunks[-1] += remaining_text

    return chunks


def get_chunks(
    doc: fitz.fitz.Document,
    chunk_token_size: Optional[int],
    return_image: Optional[bool] = True,
    return_table: Optional[bool] = True,
) -> List[dict]:
    """
    Splits a Document into chunks of specified size and returns a list of dictionaries,
    where each dictionary contains the text of a chunk and its associated metadata,
    such as images and tables.

    Args:
      doc (Document): The Document to be split into chunks.
      chunk_token_size (Optional[int]): The number of tokens to include in each chunk.
        If not specified, the default chunk size is used.
      return_image (Optional[bool]): Whether to include images in the metadata of each chunk.
      return_table (Optional[bool]): Whether to include tables in the metadata of each chunk.

    Returns:
      List[dict]: A list of dictionaries, where each dictionary contains the text of a chunk
        and its associated metadata, such as images and tables.
    """
    chunks = []
    begin_page = 1
    text = ""
    chunk_size = chunk_token_size or CHUNK_SIZE
    for index, page in enumerate(doc):
        text += page.get_text(sort=True)
        tokens = tokenizer.encode(text)
        num_tokens = len(tokens)
        if return_image:
            images = [
                doc.extract_image(img[0])["image"]
                for img in page.get_images(full=True)
                if img[0] is not None
            ]
        else:
            images = []

        if return_table:
            tbs = page.find_tables()
            tables = (
                [tb.to_pandas().to_html() for tb in tbs] if len(tbs.tables) > 0 else []
            )
        else:
            tables = []

        while num_tokens >= chunk_size:
            chunk_text = tokenizer.decode(tokens[:chunk_size])
            chunk = {
                "text": chunk_text,
                "metadata": {
                    "images": images,
                    "tables": tables,
                    "page": f"{begin_page}-{index+1}",
                },
            }
            chunks.append(chunk)
            tokens = tokens[chunk_size:]
            text = text[len(chunk_text) :]
            num_tokens = len(tokens)
            begin_page = index + 1

        if index == len(doc) - 1 and num_tokens > MIN_CHUNK_LENGTH_TO_EMBED:
            chunk_text = tokenizer.decode(tokens[:chunk_size])
            chunk = {
                "text": chunk_text,
                "metadata": {
                    "images": images,
                    "tables": tables,
                    "page": f"{begin_page}-{index+1}",
                },
            }
            chunks.append(chunk)
            text = ""
    return chunks


def create_document_chunks(
    doc: Document, chunk_token_size: Optional[int]
) -> Tuple[List[DocumentChunk], str]:
    """
    Create a list of document chunks from a document object and return the document id.

    Args:
      doc: The document object to create chunks from. It should have a text attribute and optionally an id and a metadata attribute.
      chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

    Returns:
      A tuple of (doc_chunks, doc_id), where doc_chunks is a list of document chunks, each of which is a DocumentChunk object with an id, a document_id, a text, and a metadata attribute,
      and doc_id is the id of the document object, generated if not provided. The id of each chunk is generated from the document id and a sequential number, and the metadata is copied from the document object.
    """

    # Generate a document id if not provided

    if isinstance(doc.doc, fitz.fitz.Document):
        chunks = get_chunks(doc, chunk_token_size, True, True)
    else:
        # Check if the document text is empty or whitespace
        if not doc.text or doc.text.isspace():
            return [], doc.id or str(uuid.uuid4())

        # Split the document text into chunks
        chunks = get_text_chunks(doc.text, chunk_token_size)

    doc_id = doc.id or str(uuid.uuid4())
    metadata = (
        DocumentChunkMetadata(**doc.metadata.__dict__)
        if doc.metadata is not None
        else DocumentChunkMetadata()
    )

    metadata.document_id = doc_id

    # Initialize an empty list of chunks for this document
    doc_chunks = []

    # Assign each chunk a sequential number and create a DocumentChunk object
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_{i}"
        metadata.images = chunk.get("metadata", {}).get("images", [])
        metadata.tables = chunk.get("metadata", {}).get("tables", [])
        metadata.page = chunk.get("metadata", {}).get("page", [])
        doc_chunk = DocumentChunk(
            id=chunk_id,
            text=chunk["text"],
            metadata=metadata,
        )
        # Append the chunk object to the list of chunks for this document
        doc_chunks.append(doc_chunk)

    # Return the list of chunks and the document id
    return doc_chunks, doc_id


def get_document_chunks(
    documents: List[Document],
    chunk_token_size: Optional[int],
) -> Dict[str, List[DocumentChunk]]:
    """
    Convert a list of documents into a dictionary from document id to list of document chunks.

    Args:
        documents: The list of documents to convert.
        chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

    Returns:
        A dictionary mapping each document id to a list of document chunks, each of which is a DocumentChunk object
        with text, metadata, and embedding attributes.
    """
    # Initialize an empty dictionary of lists of chunks
    chunks: Dict[str, List[DocumentChunk]] = {}

    # Initialize an empty list of all chunks
    all_chunks: List[DocumentChunk] = []

    chunk_size = chunk_token_size or CHUNK_SIZE

    # Loop over each document and create chunks
    for doc in documents:
        doc_chunks, doc_id = create_document_chunks(doc, chunk_size)

        # Append the chunks for this document to the list of all chunks
        all_chunks.extend(doc_chunks)

        # Add the list of chunks for this document to the dictionary with the document id as the key
        chunks[doc_id] = doc_chunks

    # Check if there are no chunks
    if not all_chunks:
        return {}

    # Get all the embeddings for the document chunks in batches, using get_embeddings
    embeddings: List[List[float]] = []
    for i in range(0, len(all_chunks), EMBEDDINGS_BATCH_SIZE):
        # Get the text of the chunks in the current batch
        batch_texts = [
            chunk.text for chunk in all_chunks[i : i + EMBEDDINGS_BATCH_SIZE]
        ]

        # Get the embeddings for the batch texts
        batch_embeddings = get_embeddings(batch_texts)

        # Append the batch embeddings to the embeddings list
        embeddings.extend(batch_embeddings)

    # Update the document chunk objects with the embeddings
    for i, chunk in enumerate(all_chunks):
        # Assign the embedding from the embeddings list to the chunk object
        chunk.embedding = embeddings[i]

    return chunks

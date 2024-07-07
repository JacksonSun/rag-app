#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Iterable, List

from config import GOOGLE_API_KEY, GOOGLE_CSE_ID
from const import (
    FILE_SUMMARY_CHARATER_LIMIT,
    FILE_SUMMARY_MODEL,
    FILE_SUMMARY_MODEL_TEMPERATURE,
    MAX_TOKENS,
    RESPONSE_MODEL,
    RESPONSE_TEMPERATURE,
)
from datastore.datastore import DataStore
from googleapiclient.discovery import build
from pydantic_schemas.document import DocumentChunk, Query
from services.openai import (
    get_completion,
    stream_chat_response,
    stream_completion_response,
)

from .prompting import (
    EXAMPLE_A,
    EXAMPLE_Q,
    FILE_SUMMARY_SYSTEM_PROMPT,
    FILE_SUMMARY_USER_PROMPT,
    OVERALL_RESPONSE_PROMPT,
    QUERY_TEMPLATE,
    SYSTEM_CHAT_TEMPLATE,
)

# from services.translate import translate  ## TODO replace with google translator


# @lru_cache(maxsize=16)
async def get_relevant_doc(query: str, datastore: DataStore):
    """
    Retrieves relevant documents from the datastore based on the given query.

    Args:
      query (str): The query to search for.
      datastore (DataStore): The datastore to search in.

    Returns:
      Tuple[List[Dict[str, Any]], int]: A tuple containing a list of relevant documents and a status code.
    """
    try:
        # translate query to english
        # query = translate(query)
        query_result = await datastore.query(queries=[Query(query=query)])
        docs = query_result[0].results

        def get_top_chunk_from_unique_doc(chunks: List[DocumentChunk]):
            unique_id = set()
            result = []
            for chunk in chunks:
                if chunk.metadata.document_id not in unique_id:
                    unique_id.add(chunk.metadata.document_id)
                    result.append(chunk)
                else:
                    continue
            return result

        docs = get_top_chunk_from_unique_doc(docs)

        return [doc.dict() for doc in docs], 200
    except Exception as e:
        print(f"Caught exception: {e}")
        return [], 13000


async def get_summary(
    query: str,
    datastore: DataStore,
    deployment_id: str = RESPONSE_MODEL,
    temperature: float = RESPONSE_TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
) -> Iterable[str]:
    """
    Given a query and a datastore, returns a summary of relevant documents.

    Args:
      query (str): The query to search for.
      datastore (DataStore): The datastore to search in.

    Returns:
      AsyncIterable[str]: An asynchronous iterable of summary strings.
    """
    docs, _ = await get_relevant_doc(query, datastore)
    summaries_from_docs = "\n".join(
        [f"{i+1}:{doc['text']}\n" for i, doc in enumerate(docs)]
    )
    prompt = OVERALL_RESPONSE_PROMPT.format(question=query, sources=summaries_from_docs)
    messages = [
        {"role": "system", "content": SYSTEM_CHAT_TEMPLATE},
        {"role": "user", "content": EXAMPLE_Q},
        {"role": "assistant", "content": EXAMPLE_A},
        {
            "role": "user",
            "content": QUERY_TEMPLATE.format(
                question=query, sources=summaries_from_docs
            ),
        },
    ]
    response = get_completion(
        messages=messages,
        prompt=prompt,
        deployment_id=deployment_id,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    if deployment_id == "text-davinci-003":
        return stream_completion_response(response)
    else:
        return stream_chat_response(response)


## TODO combine get_web_summary adn get_file_summary into one function


def generate_summary(
    text: str,
    deployment=FILE_SUMMARY_MODEL,
    temperature=FILE_SUMMARY_MODEL_TEMPERATURE,
    max_tokens=MAX_TOKENS,
) -> Iterable[str]:
    messages = [
        {"role": "system", "content": FILE_SUMMARY_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": FILE_SUMMARY_USER_PROMPT.format(
                input_text=text[:FILE_SUMMARY_CHARATER_LIMIT]
            ),
        },
    ]
    response = get_completion(
        messages=messages,
        deployment_id=deployment,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    return stream_chat_response(response)


def search_external_source(query: str, **kwargs):
    """search_external_source: Search external website which user provided through Google search API

    Args:
        query (str): search query
        **kwargs: variable parameters, contains result_num, etc.

    Returns:
        list: res_list
    """
    try:
        res_list = []
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query.strip(), cx=GOOGLE_CSE_ID, **kwargs).execute()
        if res and "items" in res.keys():
            for item in res["items"]:
                r = {
                    "title": item.get("title", None),
                    "snippet": item.get("htmlSnippet", None),
                    "url": item.get("link", None),
                }
                res_list.append(r)
        return res_list, 200
    except Exception:
        return None, 14000

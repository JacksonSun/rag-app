#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import openai
from typing import List, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

from config import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    OPENAI_API_TYPE,
    OPENAI_API_VERSION,
    OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
)

openai.api_base = OPENAI_API_BASE
openai.api_key = OPENAI_API_KEY
openai.api_version = OPENAI_API_VERSION
openai.api_type = OPENAI_API_TYPE


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to get the embeddings
    # NOTE: Azure Open AI requires deployment id
    deployment = OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME

    response = {}
    if deployment == None:
        response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    else:
        response = openai.Embedding.create(input=texts, deployment_id=deployment)

    # Extract the embedding data from the response
    data = response["data"]  # type: ignore

    # Return the embeddings as a list of lists of floats
    return [result["embedding"] for result in data]


from typing import List
from tenacity import retry, wait_random_exponential, stop_after_attempt


def get_completion(
    messages: Optional[List[dict]],
    prompt: Optional[str] = None,
    deployment_id: str = None,
    temperature: float = 0,
    max_tokens: int = 1024,
    stream: bool = False,
) -> dict:
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
      messages (Optional[List[dict]]): The list of messages in the chat history. message and prompt must be mutually exclusive.
      prompt (Optional[str]): The prompt to use for the completion. message and prompt must be mutually exclusive.
      deployment_id (str): The ID of the deployment to use for the completion.
      temperature (float): The temperature to use for the completion.
      max_tokens (int): The maximum number of tokens to generate for the completion.
      stream (bool): Whether to stream the response or not.

    Returns:
      dict: A dictionary containing the response from the OpenAI API.

    Raises:
      Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    # Note: Azure Open AI requires deployment id
    if deployment_id == "text-davinci-003":
        response = openai.Completion.create(
            deployment_id=deployment_id,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
    elif deployment_id in ["gpt-35-turbo-0301", "gpt-4-8k-0314"]:
        response = openai.ChatCompletion.create(
            deployment_id=deployment_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stream=stream,
        )
    else:
        raise Exception(
            "Invalid model name, please choose from text-davinci-003, gpt-35-turbo-0301, gpt-4-8k-0314"
        )
    return response


def stream_chat_response(response: dict[any, any]):
    """
    A generator function that yields the content of the first choice in the response chunks.

    Args:
      response (dict): A dictionary containing the response chunks.

    Yields:
      str: The content of the first choice in the response chunks.
    """
    for chunk in response:
        if chunk is not None:
            content = chunk["choices"][0]["delta"].get("content", None)
            if content is not None:
                yield content


def stream_completion_response(response):
    """
    A generator function that yields the text content of the first choice in each chunk of a response.

    Args:
      response (iterable): An iterable containing chunks of response data.

    Yields:
      str: The text content of the first choice in each chunk of the response.

    """
    for chunk in response:
        if chunk is not None:
            content = chunk["choices"][0]["text"]
            if content is not None:
                yield content


def get_llm(deployment, temperature, max_tokens):
    """get_llm: create a chat OpenAI connection.

    Args:
        deployment (str): OpenAI deployment name
        temperature (float): temperature of the model
        max_tokens (int): the maximum number of text token

    Raises:

    Returns:
        AzureChatOpenAI: llm
    """
    temperature = min(temperature, 1) if temperature > 1 else max(temperature, 0)
    max_tokens = min(max_tokens, 1000) if max_tokens > 1000 else max(max_tokens, 0)
    try:
        llm = AzureChatOpenAI(
            deployment_name=deployment,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_base=OPENAI_API_BASE,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_key=OPENAI_API_KEY,
            openai_api_version=OPENAI_API_VERSION,
        )
        return llm
    except Exception:
        return None


def get_streaming_llm(deployment, temperature, max_tokens):
    """get_streaming_llm: create a chat OpenAI connection with streaming and callback function

    Args:
        deployment (str): OpenAI deployment name
        temperature (float): temperature of the model
        max_tokens (int): the maximum number of text token

    Raises:

    Returns:
        AzureChatOpenAI: llm
        AsyncIteratorCallbackHandler: callback
    """
    temperature = min(temperature, 1) if temperature > 1 else max(temperature, 0)
    max_tokens = min(max_tokens, 1000) if max_tokens > 1000 else max(max_tokens, 0)
    callback = AsyncIteratorCallbackHandler()
    try:
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
    except Exception:
        return None, None


def get_embedding_llm():
    """get_embedding_llm: create an embedding OpenAI connection

    Args:

    Raises:

    Returns:
        OpenAIEmbeddings: embedding_model

    """
    try:
        embedding_model = OpenAIEmbeddings(
            deployment=OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
            openai_api_base=OPENAI_API_BASE,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_key=OPENAI_API_KEY,
        )
        return embedding_model
    except Exception:
        return None

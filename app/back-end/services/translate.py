#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import uuid
from tenacity import retry, wait_random_exponential, stop_after_attempt
from config import TRANSLATE_KEY, TRANSLATE_EP, TRANSLATE_LOCATION, TRANSLATE_PATH


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def translate(s: str) -> str:
    """Translate API

    Args:
        s (str): original text

    Returns:
        str: translated text
    """
    if s.isascii():
        return s
    else:
        constructed_url = TRANSLATE_EP + TRANSLATE_PATH
        params = {"api-version": "3.0", "from": "zh", "to": "en"}

        headers = {
            "Ocp-Apim-Subscription-Key": TRANSLATE_KEY,
            # location required if you're using a multi-service or regional (not global) resource.
            "Ocp-Apim-Subscription-Region": TRANSLATE_LOCATION,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # You can pass more than one object in body.
        body = [{"text": s}]

        request = requests.post(
            constructed_url, params=params, headers=headers, json=body
        )
        response = request.json()
        return response[0]["translations"][0]["text"]

import json

import requests
from config import EFLOW_API_URL


def get_eflow_data(domain: str, params: dict) -> dict:
    """
    Sends a POST request to the specified domain with the given parameters and returns the response data as a dictionary.

    Args:
    - domain (str): The domain to send the request to.
    - params (dict): The parameters to include in the request payload.

    Returns:
    - dict: The response data as a dictionary.

    Raises:
    - Exception: If the request fails or the user is not found.
    """

    try:
        url = EFLOW_API_URL + domain
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(params)
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        if response.status_code == 200:
            if len(data["UserID"]) == 0:
                raise Exception("User not found")
            else:
                return data
        else:
            raise Exception(data["Message"])
    except Exception as e:
        raise e

import json

import requests

url = "http://localhost:8000/completion/"
data = {"domain": "EMI", "query": "Write a song about sparkling water."}

headers = {"Content-type": "application/json"}
with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)

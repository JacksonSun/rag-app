import requests
import json

# data = {
#     "domain": "all",
#     "query": "What would be the solution for EMI failure at 150kHz?",
# }
# headers = {"Content-type": "application/json"}
# response = requests.post(
#     "http://127.0.0.1:8000/summary", stream=True, data=json.dumps(data), headers=headers
# )

data = {
    "query": "What would be the solution when EMI failure happens at 150 kHz?",
    "url": "https://www.ti.com/lit/slyy200",
}
headers = {"Content-type": "application/json"}
response = requests.post(
    "http://127.0.0.1:8000/webpage_summary/",
    stream=True,
    data=json.dumps(data),
    headers=headers,
)
for chunk in response.iter_content(1024):
    print(chunk)

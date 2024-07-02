from googleapiclient.discovery import build

my_api_key = "AIzaSyBkylbPbc8XfFZsNjTQgxGcxcJauojMHJE"
my_cse_id = "c1bd40c67063e4a1d"


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res["items"]


results = google_search(
    "what would be the solution when EMI failure happens at 150 KHz",
    my_api_key,
    my_cse_id,
    num=10,
)

if __name__ == "__main__":
    query = "what would be the solution when EMI failure happens at 150 KHz"
    results = google_search(query, my_api_key, my_cse_id, num=10)
    for res in results:
        print(res)

from elasticsearch import Elasticsearch

ELASTICSEARCH_CLOUD_ID = "Search-Elastic:c291dGhlYXN0YXNpYS5henVyZS5lbGFzdGljLWNsb3VkLmNvbSRiZDRjNjRmNTAzMTk0ZDNiOTdhNTdiMTcxMmU4YmQxNiQ5YjM5YWQ5MzJhMTk0MTU1OGVjYzkyNzVlZmZjMWYzZg=="
ELASTICSEARCH_API_KEY = "SUM0blJZb0JXNEFhNk04c09UNzU6WEFERThVbC1SQldoRkY2eS1kZVE5QQ=="
es = Elasticsearch(cloud_id=ELASTICSEARCH_CLOUD_ID, api_key=(ELASTICSEARCH_API_KEY))
es.info()

import pandas as pd
import numpy as np
import sys

sys.path.append("../")
from llms import *

qa_baseline = pd.read_csv("qa_pair.csv")


def pretty_response(response):
    result = []
    for hit in response["hits"]["hits"]:
        result.append(
            {
                "id": hit["_id"],
                "doc_id": hit["_source"]["uuid"],
                "score": hit["_score"],
                "filename": hit["_source"]["filename"],
            }
        )
    return result


def get_unique_list(my_list):
    unique_list = []
    seen = set()

    for item in my_list:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list


def get_all_summary():
    response = es.search(index="rd_expert", size=500, query={"match_all": {}})
    result = []
    for hit in response["hits"]["hits"]:
        result.append(
            {
                "doc_id": hit["_source"]["uuid"],
                "filename": hit["_source"]["filename"],
                "summary": hit["_source"]["summary"],
            }
        )
    summary_dict = {}
    for doc in result:
        summary_dict[doc["doc_id"]] = doc["summary"]
    return summary_dict


def get_relevant_and_evaluate(
    qa_baseline=qa_baseline, q_col="query", r_col="similarity_search"
):
    df = qa_baseline.copy()
    r = []
    scores = []
    for index, row in df.iterrows():
        q = row[q_col]
        actual = row["source"]
        response = es.search(
            index="rd_expert_hybrid",
            size=10,
            query={
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": q,
                                "fields": ["filename^3", "content"],
                                "type": "phrase",
                            }
                        },
                        {
                            "multi_match": {
                                "query": q,
                                "fields": ["filename^3", "content"],
                                "type": "most_fields",
                                "tie_breaker": 0.8,
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                    "boost": 0.8,
                }
            },
            knn={
                "field": "embedding",
                "query_vector": embed_model.embed_query(q),
                "k": 10,
                "num_candidates": 50,
                "boost": 0.2,
            },
            rank={
                "rrf": {
                    "window_size": 20,
                }
            },
        )
        doc_list = get_unique_list(
            pd.DataFrame.from_records(pretty_response(response))["filename"].values
        )
        if actual.strip() in doc_list[:4]:
            scores.append(1)
        # elif actual.strip()  == doc_list[1]:
        #     scores.append(0.75)
        # elif actual.strip()  == doc_list[2]:
        #     scores.append(0.5)
        # elif actual.strip()  == doc_list[3]:
        #     scores.append(0.25)
        else:
            scores.append(0)
        r.append(doc_list)
    df[r_col] = r
    df["score"] = scores
    return df, np.mean(scores)


if __name__ == "__main__":
    res, score = get_relevant_and_evaluate()
    print(score)

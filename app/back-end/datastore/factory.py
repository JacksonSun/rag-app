#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from datastore.datastore import DataStore
from config import DATASTORE


async def get_datastore() -> DataStore:
    assert DATASTORE is not None

    match DATASTORE:
        case "elasticsearch":
            from datastore.providers.elasticsearch_datastore import (
                ElasticsearchDataStore,
            )

            return ElasticsearchDataStore()
        case _:
            raise ValueError(
                f"Unsupported vector database: {DATASTORE}. "
                f"Try one of the following: elasticsearch"
            )

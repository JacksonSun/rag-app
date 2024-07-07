#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
from datetime import datetime

from db.init_db import init_db
from kafka import KafkaProducer


def get_postgre_conn():
    db = init_db()
    try:
        return db
    except Exception as e:
        raise ("Get postgre connection faild", e)
    finally:
        db.close()


def base_response(data):
    return {"response": data}


def get_keys_from_value(dic, val):
    return [
        v["contact"]
        for k, v in dic.items()
        if k != "Update_Time" and val == v["filename"]
    ]


REMOVE_PHRASE = ["POWER SBG, LITEON TECHNOLOGY", "LITEON", "LiteOn Proprietary"]


def remove_lines(text: str, min_words: str):
    def is_valid_line(line: str):
        words = line.split()
        return len(words) >= min_words and any(word.isalpha() for word in words)

    lines = text.split("\n")
    # remove duplicate lines
    unique_lines = set()
    filtered_lines = []
    for line in lines:
        if is_valid_line(line) and line not in unique_lines:
            unique_lines.add(line)
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


def data_clean(s: str) -> str:
    # lower case and remove whitespace
    r = s.lower().strip()
    # remove unwanted characters
    r = r.translate(str.maketrans("", "", '!"#$&@[\\]^`{|}?'))
    # remove rows less than 3 words
    r = remove_lines(s, min_words=4)
    # remove POWER SBG, LITEON TECHNOLOGY (slogan)
    for key_word in REMOVE_PHRASE:
        r = r.replace(key_word, "")

    # remove multiple spaces
    # r = re.sub('\s+', ' ', r).strip()
    return r


def clean_db_response(obj) -> dict:
    """clean_db_response: Filter response from postgres db into dict object so it can be JSON serialized into API response.
    - Remove all keys that start with "_" (internal use only)

    _filter(val): filter value based on type
    - Convert None into None
    - Convert datetime object into string
    - Convert all other objects (non int or str) into string

    Args:
        obj (db.model): defined class in db.model
    """

    def _filter(val):
        if val is None:
            return val
        elif type(val) in [int, str]:
            return val
        elif type(val) is datetime:
            return val.strftime("%Y-%m-%d")  # "YYYY-MM-DD"
        else:
            return str(val)

    filtered_dict = {}
    for k, v in obj.items():
        if not k.startswith("_"):
            filtered_dict[k] = _filter(v)

    return filtered_dict


def convert_datetime_to_str(obj) -> dict:
    for k, v in obj.items():
        if k in ["create_time", "last_modified"]:
            date_obj = datetime.fromisoformat(v)
            obj[k] = date_obj.strftime("%Y-%m-%d")  # "YYYY-MM-DD"
    return obj


def get_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers="kafka-kh-01.liteon.com:9093",
        api_version=(0, 11, 5),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    return producer


def get_contact_person_from_filename(filename: str) -> str:
    """
    Extracts the contact person's name from a given filename.

    Args:
    - filename (str): The name of the file to extract the contact person's name from.
    filename = YYYYMMDD[XX_XX_ContactPerson]_XXXXX.pdf

    Returns:
    - str: The contact person's name extracted from the filename.
    """
    return filename.split("[")[1].split("]")[0].split("_")[-1]

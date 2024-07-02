#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from kafka import KafkaConsumer
from kafka import KafkaProducer
import json


def test_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers="kafka-kh-01.liteon.com:9093",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    consumer.subscribe(topics="rd_expert_pipeline")
    for message in consumer:
        print("%d:%d: v=%s" % (message.partition, message.offset, message.value))


def test_producer():
    producer = KafkaProducer(
        bootstrap_servers="kafka-kh-01.liteon.com:9093",
        api_version=(0, 11, 5),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(
        "rd_expert_pipeline",
        value={
            "uuid": "aaa",
            "file_name": "xxxx",
            "blob_url": "zzzzzzzz",
        },
    )
    producer.flush()


if __name__ == "__main__":
    test_producer()

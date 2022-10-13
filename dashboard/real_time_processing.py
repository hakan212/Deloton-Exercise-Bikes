"""This module contains the refresh_data function, which ingests data from our kafka stream to
serve the live section of the dashboard"""

import os

from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()
import uuid

import real_time_helpers

KAFKA_SERVER = os.getenv("KAFKA_SERVER")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME")

current_data = {}

c = Consumer(
    {
        "bootstrap.servers": KAFKA_SERVER,
        "group.id": f"deleton" + str(uuid.uuid1()),
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": KAFKA_USERNAME,
        "sasl.password": KAFKA_PASSWORD,
        "session.timeout.ms": 6000,
        "heartbeat.interval.ms": 1000,
        "fetch.wait.max.ms": 6000,
        "auto.offset.reset": "latest",
        "enable.auto.commit": "false",
        "max.poll.interval.ms": "86400000",
        "topic.metadata.refresh.interval.ms": "-1",
        "client.id": "id-002-005",
    }
)

c.subscribe([KAFKA_TOPIC_NAME])


def refresh_data():
    global current_data
    kafka_message = c.poll(
        0.5
    )  # poll all messages that have occurred since last refresh

    if kafka_message is not None:  # ensure we have a message
        log = kafka_message.value().decode("utf-8")

        if "INFO" in log:  # only check for strings with INFO
            real_time_helpers.update_current_ride_metrics(current_data, log)

        if "SYSTEM" in log:
            real_time_helpers.update_current_rider_information(current_data, log)

        if "-------" in log or "Getting user data from server" in log:
            current_data = {}

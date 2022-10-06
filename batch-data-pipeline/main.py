import json
import os
import uuid
from statistics import mean

from confluent_kafka import Consumer
from dotenv import load_dotenv

from data_cleaning import *
from log_processing import *
from snowflake_connection import *

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_SERVER")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME")


def subscribe_to_kafka_topic():
    """Produce a consumer that subscribes to the relevant Kafka topic"""
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
    return c


def polling_kafka():
    """Polls kafka in an infinite loop, making insert queries into snowflake tables once data processing has finished"""
    wait_for_first_user = (
        True  # Wait for current user to finish, so can obtain all relevant information
    )
    first_user_collected = (
        False  # Add check for first user so data is not sent to snowflake prematurely
    )

    consumer = subscribe_to_kafka_topic()
    cs = connect_to_snowflake()

    resistance_list = []
    power_list = []
    heart_rate_list = []
    rpm_list = []

    while True:

        kafka_message = consumer.poll(0.5)

        if wait_for_first_user:
            kafka_message = wait_for_system_log(consumer)
            wait_for_first_user = False

        if kafka_message is not None:  # exclude none values
            log = kafka_message.value().decode("utf-8")

            if "SYSTEM" in log:
                first_user_collected = True #After it has finished waiting for the first user, the first system log that comes in is the next user
                                            #hence first user is collected, which is important when extracting data in the 'new ride' condition
                begin_timestamp, user_dictionary = dict_from_system_log(log)

            elif "INFO" in log:  # only check for strings with INFO

                values = json.loads(log)
                log = values.get("log")

                if "Ride" in log:  # process strings with Ride info
                    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Ride - "
                    timestamp_and_values = log.split(split_by_timestamp_and_logs)

                    log_values = extract_values_from_log(timestamp_and_values[1])

                    duration = int(float(log_values[0]))
                    resistance_list.append(int(log_values[1]))

                elif "Telemetry" in log:
                    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Telemetry - "
                    timestamp_and_values = log.split(split_by_timestamp_and_logs)

                    log_values = extract_values_from_log(timestamp_and_values[1])

                    heart_rate_list.append(int(log_values[0]))
                    rpm_list.append(int(log_values[1]))
                    power_list.append(round(float(log_values[2]), 3))

            elif (
                "new ride" in log and first_user_collected
            ):  # New user is starting, so load collected data into snowflake and reset
                total_power = sum(power_list)
                mean_power = mean(power_list)
                mean_rpm = mean(rpm_list)
                mean_heart_rate = mean(heart_rate_list)
                mean_resistance = mean(resistance_list)

                insert_into_users(cs, user_dictionary)
                insert_into_rides(
                    cs,
                    user_dictionary,
                    begin_timestamp,
                    duration,
                    total_power,
                    mean_power,
                    mean_resistance,
                    mean_rpm,
                    mean_heart_rate,
                )

                power_list = []
                rpm_list = []
                heart_rate_list = []
                resistance_list = []


polling_kafka()

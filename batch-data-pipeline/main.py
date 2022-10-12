import json
import os
from statistics import mean

from dotenv import load_dotenv

import insert_queries
import log_processing
from assets.pipeline_engine_wrapper import databaseConnection
from kafka_consumer import subscribe_to_kafka_topic

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def polling_kafka():
    """Polls kafka in an infinite loop, making insert queries into snowflake tables once data processing has finished"""
    wait_for_first_user = (
        True  # Wait for current user to finish, so can obtain all relevant information
    )
    first_user_collected = (
        False  # Add check for first user so data is not sent to snowflake prematurely
    )

    consumer = subscribe_to_kafka_topic()
    conn = databaseConnection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

    resistance_list, power_list, heart_rate_list, heart_rate_list = [], [], [], []

    while True:

        kafka_message = consumer.poll(0.5)

        if wait_for_first_user:
            kafka_message = log_processing.wait_for_system_log(consumer)
            wait_for_first_user = False

        if kafka_message is not None:  # exclude none values
            log = kafka_message.value().decode("utf-8")

            if "SYSTEM" in log:
                first_user_collected = True  # After it has finished waiting for the first user, the first system log that comes in is the next user
                # hence first user is collected, which is important when extracting data in the 'new ride' condition

                begin_timestamp, user_dictionary = log_processing.dict_from_system_log(
                    log
                )

            elif "INFO" in log:  # only check for strings with INFO

                values = json.loads(log)
                log = values.get("log")

                duration = update_current_ride_info(resistance_list, power_list, heart_rate_list, rpm_list, log)

            elif (
                "new ride" in log and first_user_collected
            ):  # New user is starting, so load collected data into snowflake and reset
                total_power = sum(power_list)
                mean_power = mean(power_list)
                mean_rpm = mean(rpm_list)
                mean_heart_rate = mean(heart_rate_list)
                mean_resistance = mean(resistance_list)

                insert_queries.insert_into_users(conn, user_dictionary)
                insert_queries.insert_into_rides(
                    conn,
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

def update_current_ride_info(resistance_list, power_list, heart_rate_list, rpm_list, log):
    if "Ride" in log:
        duration = update_duration_and_resistance(resistance_list, log)

    elif "Telemetry" in log:
        update_heart_rpm_power(power_list, heart_rate_list, rpm_list, log)
    return duration

def update_heart_rpm_power(power_list, heart_rate_list, rpm_list, log):
    """
    Appends latest values to power, rpm & heart rate lists given a log containing
    telemetry info.
    """
    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Telemetry - "
    timestamp_and_values = log.split(split_by_timestamp_and_logs)

    log_values = log_processing.extract_values_from_log(
                        timestamp_and_values[1]
                    )

    heart_rate_list.append(int(log_values[0]))
    rpm_list.append(int(log_values[1]))
    power_list.append(round(float(log_values[2]), 3))

def update_duration_and_resistance(resistance_list, log):
    """
    Appends latest resistance value to resistance_list & returns latest duration value
    when provided with a log containing ride info.
    """

    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Ride - "
    timestamp_and_values = log.split(split_by_timestamp_and_logs)

    log_values = log_processing.extract_values_from_log(
                        timestamp_and_values[1]
                    )
    
    # Duration is first value to appear in the log and resistance is the second
    duration = int(float(log_values[0]))
    resistance_list.append(int(log_values[1]))
    return duration


polling_kafka()

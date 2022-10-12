import json
import re

import data_cleaning


def extract_values_from_log(string):
    """Extract numerical values from Kafka log using regular expression"""
    regexp = r"\d+.?\d+|\d"
    numerical_values = re.findall(regexp, string)
    return numerical_values


def wait_for_system_log(consumer):
    """Waits for current user when starting script to finish their ride, as their user data is not retrievable"""
    print("Waiting for first user to finish... This may take some time.")
    while True:
        kafka_message = consumer.poll(0.5)
        if kafka_message is not None:
            kafka_log = kafka_message.value().decode("utf-8")

            if "SYSTEM" in kafka_log:
                print("First user has finished, now beginning data processing")
                return kafka_message


def dict_from_system_log(log):
    """Obtains user dictionary from system log"""
    system_log = json.loads(log).get("log")
    split_log = system_log.split(" mendoza v9: [SYSTEM] data = ")
    begin_timestamp = split_log[0][
        :-7
    ]  # remove milliseconds from timestamp

    dictionary_string = split_log[1][:-1]
    user_dictionary = json.loads(dictionary_string)

    user_dictionary = data_cleaning.clean_user_data(user_dictionary)
    return begin_timestamp, user_dictionary

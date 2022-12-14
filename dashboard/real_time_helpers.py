"""This module contains helpers for refresh_data function in real_time_processing, which ingests
data from our kafka stream to serve the live section of the dashboard"""


import datetime
import json
import re
from datetime import date

import pandas as pd


def update_duration_and_resistance(
    current_data: dict, duration_and_resistance: list
) -> None:
    """Will update current_data given [duration, resistance]"""
    duration = duration_and_resistance[0]
    resistance = duration_and_resistance[1]

    current_data["duration"] = float(duration)
    current_data["resistance"] = int(resistance)


def update_heart_rpm_and_power(current_data: dict, heart_rpm_and_power: list) -> None:
    """Will update current_data given [heart, rpm, power]"""
    heart_rate = int(heart_rpm_and_power[0])
    rpm = int(heart_rpm_and_power[1])
    power = round(float(heart_rpm_and_power[2]), 2)

    current_data["heart_rate"] = heart_rate
    if current_data.get("heart_rates") is None:
        current_data["heart_rates"] = pd.Series(dtype="float64")
    current_data["heart_rates"][current_data["duration"]] = heart_rate
    current_data["rpm"] = rpm
    current_data["power"] = power


def update_current_ride_metrics(current_data: dict, log: str) -> None:
    """Will update current_data given log containing information on the current ride"""
    values = json.loads(log)
    new_log = values.get("log")

    if "Ride" in new_log:  # process strings with Ride info
        new_log = new_log.split(" mendoza v9: [INFO]: Ride - ")
        timestamp = new_log[0]
        current_data["timestamp"] = timestamp

        duration_and_resistance = re.findall(r"\d+.?\d+|\d", new_log[1])
        update_duration_and_resistance(current_data, duration_and_resistance)

    if "Telemetry" in new_log:
        new_log = new_log.split(" mendoza v9: [INFO]: Telemetry - ")
        timestamp = new_log[0]
        current_data["timestamp"] = timestamp

        heart_rpm_and_power = re.findall(r"\d+.?\d+|\d", new_log[1])
        update_heart_rpm_and_power(current_data, heart_rpm_and_power)


def convert_epoc_milliseconds_to_dob(epoc_milliseconds: int) -> datetime.datetime:
    epoc_seconds = epoc_milliseconds / 1000

    return datetime.datetime.fromtimestamp(epoc_seconds)


def calculate_age(born: datetime.datetime) -> int:
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def update_user_information(current_data: dict, user_information: str) -> None:
    """Given string from log on new user, will update current_data user information"""
    current_data["user_id"] = int(re.findall('"user_id":(\d+)', user_information)[0])
    current_data["user_name"] = re.findall(
        '"name":"(\w+ \w+ \w+|\w+ \w+)', user_information
    )[0]
    current_data["user_gender"] = re.findall('"gender":"(\w+)', user_information)[0]
    current_data["user_address"] = re.findall('"address":"([\w ,]+)', user_information)[
        0
    ]
    current_data["user_email"] = re.findall(
        '"email_address":"(.+@\w+.\w+)"', user_information
    )[0]
    current_data["user_height"] = int(
        re.findall('"height_cm\\":(\d+)', user_information)[0]
    )
    current_data["user_weight"] = int(
        re.findall('"weight_kg\\":(\d+)', user_information)[0]
    )
    current_data["user_account_created"] = int(
        re.findall('"account_create_date":(\d+)', user_information)[0]
    )
    current_data["user_bike_serial"] = re.findall(
        '"bike_serial":"(\w+)', user_information
    )[0]

    user_dob_epoc = int(re.findall('"date_of_birth\\":([-\d]+)', user_information)[0])
    user_dob = convert_epoc_milliseconds_to_dob(user_dob_epoc)
    current_data["user_dob"] = user_dob
    current_data["user_age"] = calculate_age(user_dob)


def update_current_rider_information(current_data: dict, log: str) -> None:
    """Updates information on current rider"""
    values = json.loads(log)
    new_log = values.get("log")
    new_log = new_log.split(" mendoza v9: [SYSTEM] data = ")

    current_data["timestamp"] = new_log[0]
    user_information = new_log[1]

    update_user_information(current_data, user_information)

import log_processing


def update_duration_and_resistance(resistance_list, log):
    """
    Appends latest resistance value to resistance_list & returns latest duration value
    when provided with a log containing ride info.
    """

    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Ride - "
    timestamp_and_values = log.split(split_by_timestamp_and_logs)

    log_values = log_processing.extract_values_from_log(timestamp_and_values[1])

    # Duration is first value to appear in the log and resistance is the second
    duration = int(float(log_values[0]))
    resistance_list.append(int(log_values[1]))
    return duration


def update_heart_rpm_power(power_list, heart_rate_list, rpm_list, log):
    """
    Appends latest values to power, rpm & heart rate lists given a log containing
    telemetry info.
    """
    split_by_timestamp_and_logs = " mendoza v9: [INFO]: Telemetry - "
    timestamp_and_values = log.split(split_by_timestamp_and_logs)

    log_values = log_processing.extract_values_from_log(timestamp_and_values[1])

    heart_rate_list.append(int(log_values[0]))
    rpm_list.append(int(log_values[1]))
    power_list.append(round(float(log_values[2]), 3))


def update_current_ride_info(
    resistance_list, power_list, heart_rate_list, rpm_list, log
):
    """Updates either ride or telemetry information given log on current ride info"""

    if "Ride" in log:
        duration = update_duration_and_resistance(resistance_list, log)

    elif "Telemetry" in log:
        update_heart_rpm_power(power_list, heart_rate_list, rpm_list, log)
    return duration

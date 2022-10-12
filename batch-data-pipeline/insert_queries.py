"""Insert queries to insert cleaned data into Aurora production schema"""
import pandas as pd #needed for .empty method


def insert_into_users(conn, user_dictionary):
    """Makes insert query into users table once all relevant information has been obtained"""
    user_df = conn.select_user(user_dictionary)

    if user_df.empty:  # Use pandas to check if result is empty
        conn.insert_users_query(user_dictionary)
        print("inserted user into table")


def insert_into_rides(
    conn,
    user_dictionary,
    begin_timestamp,
    duration,
    total_power,
    mean_power,
    mean_resistance,
    mean_rpm,
    mean_heart_rate,
):
    """Insert ride into rides table"""
    conn.insert_rides_query(
        user_dictionary,
        begin_timestamp,
        duration,
        total_power,
        mean_power,
        mean_resistance,
        mean_rpm,
        mean_heart_rate,
    )

    print("inserted ride into table")

"""Generates graphs for pdf report by querying last 12 hours of data using data mart. The graphs are produced using the plotly library
and data values are obtained by performing aggregate functions on the data."""

import os
from datetime import date

import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
PRODUCTION_SCHEMA = os.getenv("PRODUCTION_SCHEMA")


def get_engine_connection():
    """Connects to postgreSQL DBMS on AWS Aurora using an SQLalchemy engine."""
    conn_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(conn_string)


def get_dataframe():
    """
    Creates a Pandas DataFrame by querying
    AWS Aurora with an SQL statement.

    Data collected is rides and users joined
    where the timestamp is within the last 24
    hours.
    """

    query = f"""
        WITH user_gender_dob AS (
            SELECT user_id, gender,
                DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))
                    AS age 
                FROM {PRODUCTION_SCHEMA}.users
        ),

        rides_before AS (
            SELECT *
                FROM {PRODUCTION_SCHEMA}.rides
                WHERE begin_timestamp >= (NOW() - INTERVAL '24 hours')
        )

        SELECT ugd.user_id, rb.ride_id, ugd.gender, ugd.age, rb.begin_timestamp,
            rb.total_duration_sec, rb.total_power, rb.mean_power, rb.mean_resistance,
                rb.mean_rpm, rb.mean_heart_rate

            FROM user_gender_dob AS ugd
            RIGHT JOIN rides_before AS rb
                ON ugd.user_id = rb.user_id
    """

    df_riders = pd.read_sql(query, con=get_engine_connection())

    return df_riders


def plot_gender_rides_pie(df_riders):
    """Plots a pie chart of the gender split of rides in the past day"""
    gender_df = df_riders["gender"].value_counts()
    gender_fig = px.pie(
        gender_df,
        values=gender_df.values,
        names=gender_df.index,
        title=f"Gender of bicycle riders for {date.today()}",
        width=500,
        height=500,
        color_discrete_sequence=["#8FBC8F", "#483D8B"],
    )

    gender_fig.write_image("/tmp/gender_fig.png")

    return gender_fig


def plot_age_rides_bar(df_riders):
    """Plots a bar chart of the ages of riders for the past day"""
    age_bin = [0, 15, 30, 45, 60, 75, 90, 105]
    age_df = df_riders["age"].value_counts(bins=age_bin, sort=False)
    age_range_list = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "90+"]

    age_bin_ticks = age_df.index.astype(str)
    age_fig = px.bar(
        x=age_bin_ticks,
        y=age_df.values,
        labels={"y": "Number of riders", "x": "Age ranges of riders"},
        width=650,
        title=f"Age ranges of bicycle riders for {date.today()}",
    )
    age_fig.update_xaxes(tickvals=age_bin_ticks, ticktext=age_range_list)
    age_fig.update_traces(marker=dict(color="#8FBC8F"))

    age_fig.write_image("/tmp/age_fig.png")

    return age_fig


def get_number_of_rides(df_riders):
    """Return the total number of rides in df_rides"""
    return len(df_riders)


def get_mean_total_power(df_riders):
    """Gets the mean total power of all riders for the past day"""
    mean_total_power = int(df_riders["total_power"].mean())
    return mean_total_power


def get_mean_power_output(df_riders):
    """Gets the mean power output per rider for the past day"""
    mean_power_output = df_riders["mean_power"].mean().round(2)
    return mean_power_output


def get_mean_heart_rate(df_riders):
    """Gets the mean heart rate per rider for the past day"""
    mean_heart_rate = df_riders["mean_heart_rate"].mean().round(1)
    return mean_heart_rate

"""This module contains the functions which generate the content for the recent rides section of
the dashboard"""

import os

import pandas as pd
import plotly.graph_objs as go # type: ignore
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

pd.set_option("plotting.backend", "plotly")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
MART_SCHEMA = os.getenv("MART_SCHEMA")

table_name = "recent_rides"


def get_engine_connection():
    """Connects to postgreSQL DBMS on AWS Aurora"""
    conn_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(conn_string)


sql_engine = get_engine_connection()


def get_recent_rides_data():
    return pd.read_sql_table(table_name, con=sql_engine, schema=MART_SCHEMA)


def create_gender_split_pie_chart(gender_related_data, title):
    """Creates a pie chart given gender related data"""

    color_scheme = ["#483D8B", "#8FBC8F"]

    gender_split_pie_chart = go.Figure(
        data=go.Pie(labels=["Female", "Male"], values=gender_related_data),
    )

    gender_split_pie_chart.update_layout(
        title_text=title,
        width=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
    )

    gender_split_pie_chart.update_traces(marker=dict(colors=color_scheme))

    return gender_split_pie_chart


def create_ride_age_groups_bar(recent_rides_data):
    """Creates a bar chart representing the number of riders per age group"""
    num_rides_by_age = (
        recent_rides_data["age"]
        .value_counts(bins=[0, 15, 30, 45, 60, 75, 90, 110])
        .sort_index()
    )
    num_rides_by_age = pd.DataFrame(
        {"age_group": num_rides_by_age.index, "num_of_riders": num_rides_by_age.values}
    )
    num_rides_by_age["age_group"] = num_rides_by_age["age_group"].astype("str")

    rides_by_age_plot = num_rides_by_age.plot(
        kind="bar",
        x="age_group",
        y="num_of_riders",
        title="Number of riders by age group",
        color_discrete_sequence=[
            "#8FBC8F",
            "#8FBC8F",
            "#8FBC8F",
            "#8FBC8F",
            "#8FBC8F",
            "#8FBC8F",
            "#8FBC8F",
        ],
    )

    rides_by_age_plot.update_layout(
        width=500,
        xaxis_title="Age Group",
        yaxis_title="Number of Riders",
        xaxis=dict(
            tickangle=90,
            tickvals=list(num_rides_by_age["age_group"]),
            ticktext=["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "90+"],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
    )

    return rides_by_age_plot


def get_total_power_recent_rides(recent_rides_data):
    """Find the total power output of riders over the past 12 hours"""
    total_power_watts = round(recent_rides_data["total_power"].sum())
    total_power_kilowatts = round(total_power_watts / 1000)

    return f"{total_power_kilowatts}kW"


def get_mean_power_recent_rides(recent_rides_data):
    """find the average power output of riders over the past 12 hours"""
    average_power = round(recent_rides_data["mean_power"].mean(), 2)
    return f"{average_power}W"

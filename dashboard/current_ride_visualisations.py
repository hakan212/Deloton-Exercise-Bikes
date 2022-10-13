"""This module contains the functions which generate the content for the current rides section of
the dashboard"""

import dash_daq as daq
import numpy as np
import plotly.express as px
import plotly.graph_objects
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import real_time_processing
import recent_rides_visualisations
from heart_rate_calculator import (calculate_max_heart_rate, heart_rate_high,
                                   heart_rate_low, heart_rate_ok)


def live_ride_gauge(data: dict) -> daq.Gauge:
    """Generates the heart rate gauge for a given user, based on the information in the data
    parameter.
    """
    age = data.get("user_age")

    if not age:
        return html.Span("Heart rate gauge unavailable without rider age data")

    ride_duration = data.get("duration") or 0
    ride_duration_minutes = int(ride_duration // 60)
    ride_duration_seconds = int(ride_duration % 60)

    max_rate = calculate_max_heart_rate(age)
    label = (
        f"{data.get('user_name')} {' ♂' if data.get('user_gender') == 'male' else ' ♀'}"
        f"- {ride_duration_minutes}m {ride_duration_seconds}s"
    )

    return daq.Gauge(
        color={
            "gradient": True,
            "ranges": {
                "white": [0, 50],
                "green": [50, max_rate - 40],
                "yellow": [max_rate - 40, max_rate],
                "red": [max_rate, 200],
            },
        },
        label=label,
        showCurrentValue=True,
        units="BPM",
        scale={"start": 0, "interval": 25, "labelInterval": 1},
        value=data.get("heart_rate") or 0,
        min=0,
        max=200,
        style={"color": "white"},
    )


def current_rider_details(data: dict) -> html.Div:
    """Returns an html span element containing text with current rider information"""
    return html.Div(
        children=[
            html.Div(f"User id: {data.get('user_id')}"),
            html.Div(f"Name: {data.get('user_name')}"),
            html.Div(f"Gender: {data.get('user_gender')}"),
            html.Div(f"Height: {data.get('user_height')} cm"),
            html.Div(f"Age: {data.get('user_age')}"),
            html.Div(f"Weight: {data.get('user_weight')} kg"),
        ]
    )


min_reading, max_reading = 100, 100


def live_heart_rate_plot(data: dict) -> plotly.graph_objects.Figure:
    """Generates live-updating scatter graph for user's heart-rate"""

    global min_reading, max_reading

    latest = data.get("heart_rate") or np.nan
    heart_rates = data.get("heart_rates")

    if heart_rates is None:  # Return empty plot if no data
        fig = px.line(template="simple_white", height=300)
    else:  # Create plot
        fig = px.line(
            x=heart_rates.index,
            y=heart_rates.values,
            template="simple_white",
            height=400,
            labels={"x": "Ride Duration (s)", "y": "Heart Rate (BPM)"},
        )
    set_line_plot_colors(fig)

    # set least and greatest values on the y-axis, adjusted to fit values read so far
    min_reading, max_reading = min(min_reading, latest), max(max_reading, latest)
    y_top, y_bottom = ((max_reading // 50) + 1) * 50, (min_reading // 50) * 50
    fig.update_layout(yaxis={"range": [y_bottom, y_top]})

    # Add surfing zookeeper if there is a latest reading
    if latest is not np.nan:
        add_surfing_zookeeper(fig, latest, y_bottom, y_top)
    return fig


def set_line_plot_colors(fig) -> None:
    """Set colors on line plot"""
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font_color": "#FFFFFF",
        }
    )
    fig.update_traces(line_color="red")
    fig.update_xaxes(linecolor="#FFFFFF")
    fig.update_yaxes(linecolor="#FFFFFF")


def add_surfing_zookeeper(
    fig: plotly.graph_objects.Figure, latest: int, y_bottom: int, y_top: int
) -> None:
    """Add surfing zookeeper to line plot"""
    # number between 0 and 1 representing height of latest point on line as fraction of graph height
    line_height = (latest - y_bottom) / (y_top - y_bottom)

    zookeper_width, zookeeper_height = 0.1, 0.15
    fig.add_layout_image(
        {
            "source": "assets/apache_zookeeper.png",
            "x": 0.925,  # zookeeper position on x-axis
            "y": line_height
            + zookeeper_height,  # zookeeper position on y-axis +0.15 offset for zookeeper height
            "sizex": zookeper_width,
            "sizey": zookeeper_height,
            "sizing": "stretch",
            "opacity": 1,
            "layer": "below",
        }
    )


def heart_rate_alert(data: dict) -> dict:
    """Will display warning message on screen if heart rate is too high or low
    Toggles the display option on the div with id heart-rate-alert
    """
    heart_rate = data.get("heart_rate")
    rider_age = data.get("user_age")

    if not rider_age or not heart_rate or heart_rate_ok(heart_rate, rider_age):
        return {"display": "none"}

    return {"display": "block"}


def heart_rate_description(data: dict) -> html.Span:
    """Determines output of heart-rate-alert-description"""
    heart_rate = data.get("heart_rate")
    rider_age = data.get("user_age")

    message = ""
    if not heart_rate or not rider_age:
        pass
    elif heart_rate_low(heart_rate, rider_age):
        message = "Heart rate too low, work harder!"
    elif heart_rate_high(heart_rate, rider_age):
        message = "Heart rate very high! Perhaps take a break or decrease intensity."
    return html.Span(message)

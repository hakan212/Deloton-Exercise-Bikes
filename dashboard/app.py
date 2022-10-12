from typing import Tuple

import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import real_time_processing
import recent_rides_visualisations
from heart_rate_calculator import (calculate_max_heart_rate, heart_rate_high,
                                   heart_rate_low, heart_rate_ok)

app = Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.COSMO],
    title="Deloton Dashboard",
)

app.layout = html.Div(
    [
        html.H1("Deloton Dashboard"),
        # Current Ride info
        html.Div(
            [
                dcc.Interval(  # Calls a callback to refresh all the live components in the div
                    id="current-ride-interval",
                    interval=1000,  # refresh frequency in milliseconds
                    n_intervals=0,  # loop counter
                ),
                html.Div(
                    "Current Ride", className="panel-title", style={"font-size": 30}
                ),
                html.Div(
                    [
                        html.H3("Current Rider Account Details"),
                        html.Div(id="current-rider-text"),
                    ]
                ),
                html.Div(
                    [html.H3("Current Ride Stats"), html.Div(id="live-ride-text")]
                ),
                html.Div(id="live-ride-gauge"),
                html.Div(
                    id="heart-rate-alert",
                    style={"display": "none"},
                    children=[
                        html.H3("HEART RATE WARNING"),
                        html.Div(id="heart-rate-alert-description"),
                    ],
                ),
            ],
            className="panel",
            id="left-panel",
        ),
        # Recent Ride info
        html.Div(
            [
                dcc.Interval(  # Calls a callback to refresh all the live components in the div
                    id="recent-rides-interval",
                    interval=5
                    * 60
                    * 1000,  # refresh frequency in milliseconds (= 5 mins)
                    n_intervals=0,  # loop counter
                ),
                html.Div(
                    "Recent Rides", className="panel-title", style={"font-size": 30}
                ),
                dcc.Graph(id="number-of-riders-gender-pie"),
                dcc.Graph(id="duration-of-ride-gender-pie"),
                dcc.Graph(id="number-of-riders-age-bar"),
                html.H3("Total Power:"),
                html.H2(id="total-power"),
                html.H3("Average Power per Rider:"),
                html.H3(id="average-power"),
            ],
            className="panel",
            id="right-panel",
        ),
    ]
)


@app.callback(
    Output("current-rider-text", "children"),
    Output("live-ride-text", "children"),
    Output("live-ride-gauge", "children"),
    Output("heart-rate-alert", "style"),
    Output("heart-rate-alert-description", "children"),
    Input("current-ride-interval", "n_intervals"),
)
def current_ride_live_refresh(n_intervals: int) -> Tuple:
    real_time_processing.refresh_data()
    data = real_time_processing.current_data
    return (
        current_rider_details(data),
        live_ride_details(data),
        live_ride_gauge(data),
        heart_rate_alert(data),
        heart_rate_description(data),
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


def live_ride_details(data: dict) -> html.Span:
    """Returns an html span element containing text with live information on the current ride"""
    ride_duration_seconds = data.get("duration")
    heart_rate = data.get("heart_rate")

    if ride_duration_seconds:
        ride_duration_minutes = int(ride_duration_seconds // 60)
        ride_duration_seconds = int(ride_duration_seconds % 60)
    else:
        ride_duration_minutes = 0
        ride_duration_seconds = 0

    message = (
        f"Riding for {ride_duration_minutes} minutes and "
        f"{ride_duration_seconds}  seconds. Heart rate: {heart_rate} BPM"
    )

    return html.Span(message)


def live_ride_gauge(data: dict):
    age, heart_rate = data.get("user_age"), data.get("heart_rate") or 0

    if not age:
        return html.Span('Heart rate gauge unavailable without rider age data')
        
    max_rate = calculate_max_heart_rate(age)
    return daq.Gauge(
        color={
            "gradient": True,
            "ranges": {
                "white": [0, 50],
                "green": [50, 100],
                "yellow": [100, max_rate],
                "red": [max_rate, 200],
            },
        },
        label="Heart Rate",
        showCurrentValue=True,
        units="BPM",
        scale={"start": 50, "interval": 25, "labelInterval": 50},
        value=heart_rate or 0,
        min=0,
        max=200,
        style={"color": "black"},
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


@app.callback(
    Output("number-of-riders-gender-pie", "figure"),
    Output("duration-of-ride-gender-pie", "figure"),
    Output("number-of-riders-age-bar", "figure"),
    Output("total-power", "children"),
    Output("average-power", "children"),
    Input("recent-rides-interval", "n_intervals"),
)
def recent_rides_live_refresh(n_intervals: int):
    """Obtains and displays visualisations & metrics on rides over past 12 hours"""
    recent_rides_data = recent_rides_visualisations.get_recent_rides_data()

    gender_count = recent_rides_data.groupby(["gender"]).count()["user_id"]
    gender_duration = recent_rides_data.groupby(["gender"]).sum()["total_duration_sec"]

    gender_count_pie = recent_rides_visualisations.create_gender_split_pie_chart(
        gender_count, "Number of Rides by Gender"
    )
    gender_duration_pie = recent_rides_visualisations.create_gender_split_pie_chart(
        gender_duration, "Total Ride Duration by Gender"
    )
    ride_age_groups_bar = recent_rides_visualisations.create_ride_age_groups_bar(
        recent_rides_data
    )
    total_power = recent_rides_visualisations.get_total_power_recent_rides(
        recent_rides_data
    )
    average_power = recent_rides_visualisations.get_mean_power_recent_rides(
        recent_rides_data
    )

    return (
        gender_count_pie,
        gender_duration_pie,
        ride_age_groups_bar,
        total_power,
        average_power,
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)

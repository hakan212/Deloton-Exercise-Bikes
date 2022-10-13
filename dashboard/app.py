from typing import Tuple

import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
import plotly.express as px
import plotly.graph_objects
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import real_time_processing
import recent_rides_visualisations
from heart_rate_calculator import (
    calculate_max_heart_rate,
    heart_rate_high,
    heart_rate_low,
    heart_rate_ok,
)

app = Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.COSMO],
    title="Deloton Dashboard",
)

app.layout = html.Div(
    [
        html.Div([html.H1("Deloton Live Dashboard")]),
        html.Div(
            [
                html.Div(
                    "Current Ride", className="panel-title", style={"font-size": 30}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Interval(  # Calls a callback to refresh all the live components in the div
                                    id="current-ride-interval",
                                    interval=1000,  # refresh frequency in milliseconds
                                    n_intervals=0,  # loop counter
                                ),
                                html.Div(
                                    "Current Ride",
                                    className="panel-title",
                                    style={"font-size": 30},
                                ),
                                html.Div(id="live-ride-gauge"),
                                dcc.Graph(id="live-heart-rate-scatter"),
                                html.Div(
                                    [
                                        html.H3("Current Rider Account Details"),
                                        html.Div(id="current-rider-text"),
                                    ]
                                ),
                                html.Div(
                                    id="heart-rate-alert",
                                    style={"display": "none"},
                                    children=[
                                        html.H3("HEART RATE WARNING"),
                                        html.Div(id="heart-rate-alert-description"),
                                    ],
                                ),
                            ],
                            className="panel_div",
                        ),
                    ],
                    className="left_panel",
                    id="left_panel",
                ),
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
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            "Recent Rides",
                                                            className="panel-title",
                                                            style={
                                                                "font-size": 30,
                                                                "height": "20%",
                                                            },
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.P(
                                                                    id="total-power"
                                                                ),
                                                            
                                                                html.P(
                                                                    id="average-power"
                                                                ),
                                                            ],
                                                            style={
                                                                "height": "80%",
                                                                "padding": "10px",
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "float": "left",
                                                        "width": "33%",
                                                    },
                                                ),
                                                html.Div(
                                                    [
                                                        dcc.Graph(
                                                            id="number-of-riders-age-bar",
                                                            style={
                                                                "width": "75%",
                                                                "height": "60%",
                                                                "padding-left": "50px",
                                                            },
                                                        )
                                                    ],
                                                    style={
                                                        "float": "right",
                                                        "width": "66%",
                                                    },
                                                ),
                                            ],
                                            style={"height": "80%"},
                                        ),
                                    ],
                                    id="top_panel",
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="number-of-riders-gender-pie",
                                            style={
                                                "display": "inline-block",
                                                "width": "45vh",
                                                "height": "45vh",
                                            },
                                        ),
                                        dcc.Graph(
                                            id="duration-of-ride-gender-pie",
                                            style={
                                                "display": "inline-block",
                                                "width": "45vh",
                                                "height": "45vh",
                                            },
                                        ),
                                    ],
                                    id="bottom_panel",
                                ),
                            ],
                            className="panel_div",
                        ),
                    ],
                    className="right_panel",
                    id="right_panel",
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("current-rider-text", "children"),
    Output("live-ride-gauge", "children"),
    Output("live-heart-rate-scatter", "figure"),
    Output("heart-rate-alert", "style"),
    Output("heart-rate-alert-description", "children"),
    Input("current-ride-interval", "n_intervals"),
)
def current_ride_live_refresh(n_intervals: int) -> Tuple:
    real_time_processing.refresh_data()
    data = real_time_processing.current_data
    return (
        current_rider_details(data),
        live_ride_gauge(data),
        live_heart_rate_plot(data),
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


def live_ride_gauge(data: dict) -> daq.Gauge:
    """Generates the heart rate gauge for a given user, based on the information in the data
    parameter.
    """
    age = data.get("user_age") or 50

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
                "green": [50, max_rate - 20],
                "yellow": [max_rate - 20, max_rate],
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


min_reading, max_reading = 100, 100


def live_heart_rate_plot(data: dict) -> plotly.graph_objects.Figure:
    """Generates live-updating scatter graph for user's heart-rate"""

    global min_reading, max_reading

    latest = data.get("heart_rate") or np.nan
    heart_rates = data.get("heart_rates")
    
    if heart_rates is None: # Return empty plot if no data
        fig = px.line(height=300)
    else: # Create plot
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
    fig.update_layout({
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font_color': "#FFFFFF"
    })
    fig.update_traces(line_color='red')
    fig.update_xaxes(linecolor='#FFFFFF')
    fig.update_yaxes(linecolor='#FFFFFF')


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
    total_power = f"""Total Power: {recent_rides_visualisations.get_total_power_recent_rides(
        recent_rides_data
    )}"""
    average_power = f"""Average Power per Rider: {recent_rides_visualisations.get_mean_power_recent_rides(
        recent_rides_data
    )}"""

    return (
        gender_count_pie,
        gender_duration_pie,
        ride_age_groups_bar,
        total_power,
        average_power,
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)

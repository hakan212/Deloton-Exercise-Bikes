from typing import Tuple

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import current_ride_visualisations
import real_time_processing
import recent_rides_visualisations

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
                                html.Div(
                                    id="heart-rate-alert",
                                    style={"display": "none"},
                                    children=[
                                        html.H3("HEART RATE WARNING"),
                                        html.Div(id="heart-rate-alert-description"),
                                    ],
                                ),
                                dcc.Graph(id="live-heart-rate-scatter"),
                                html.Div(
                                    [
                                        html.H3("Current Rider Account Details"),
                                        html.Div(id="current-rider-text"),
                                    ]
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
    Output("live-ride-gauge", "children"),
    Output("heart-rate-alert", "style"),
    Output("live-heart-rate-scatter", "figure"),
    Output("current-rider-text", "children"),
    Output("heart-rate-alert-description", "children"),
    Input("current-ride-interval", "n_intervals"),
)
def current_ride_live_refresh(n_intervals: int) -> Tuple:
    real_time_processing.refresh_data()
    data = real_time_processing.current_data
    return (
        current_ride_visualisations.live_ride_gauge(data),
        current_ride_visualisations.heart_rate_alert(data),
        current_ride_visualisations.live_heart_rate_plot(data),
        current_ride_visualisations.current_rider_details(data),
        current_ride_visualisations.heart_rate_description(data),
    )


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

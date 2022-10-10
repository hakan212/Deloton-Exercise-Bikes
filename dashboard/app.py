import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import real_time_processing
from heart_rate_calculator import heart_rate_high, heart_rate_low, heart_rate_ok

app = Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    [
        html.H1("Deloton Dashboard"),
        # Current Ride info
        html.Div(
            [
                html.H2("Current Ride"),
                html.Div(
                    [
                        html.H3("Current Rider Account Details"),
                        html.Div(id="current-rider-text"),
                        dcc.Interval(
                            id="current_rider_interval",
                            interval=0.5 * 1000,
                            n_intervals=0,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H3("Current Ride Stats"),
                        html.Div(id="live-ride-text"),
                        dcc.Interval(
                            id="live-ride-interval",
                            interval=0.5 * 1000,  # in milliseconds
                            n_intervals=0,  # counter for number of refreshes
                        ),
                    ]
                ),
                html.Div(
                    id="heart-rate-alert",
                    style={"display": "none"},
                    children=[
                        html.H3("HEART RATE WARNING"),
                        html.Div(id="heart-rate-alert-description"),
                        dcc.Interval(
                            id="heart-rate-alert-interval",
                            interval=0.5 * 1000,  # in milliseconds
                            n_intervals=0,  # counter for number of refreshes
                        ),
                    ],
                ),
            ],
        className='panel', id='left-panel'),
        # Recent Ride info
        html.Div([html.H2("Recent Rides")]
        , className='panel', id='right-panel'
        )
    ]
)


@app.callback(
    Output("current-rider-text", "children"),
    Input("current_rider_interval", "n_intervals"),
)
def current_rider_details(n_intervals: int) -> html.Span:
    """Returns an html span element containing text with current rider information

    Args:
        n_intervals: A  loop counter. Not used in the function body, but dash requires you to have
        it for the function to be called in repeatedly.
    """
    data = real_time_processing.current_data

    message = f"""User id: {data.get('user_id')}
        Name: {data.get('user_name')}
        Gender: {data.get('user_gender')}
        Height: {data.get('user_height')}cm
        Age: {data.get('user_age')}
        Weight: {data.get('user_weight')}kg"""

    return html.Span(message)


@app.callback(
    Output("live-ride-text", "children"), Input("live-ride-interval", "n_intervals")
)
def live_ride_details(n_intervals: int) -> html.Span:
    """Returns an html span element containing text with live information on the current ride

    Args:
        n_intervals: A  loop counter. Not used in the function body, but dash requires you to have
        it for the function to be called in repeatedly.
    """
    real_time_processing.refresh_data()
    ride_duration_total_seconds = real_time_processing.current_data.get(
        "duration"
    )  # or 0
    heart_rate = real_time_processing.current_data.get("heart_rate")  # or 0

    if ride_duration_total_seconds:
        ride_duration_minutes = int(ride_duration_total_seconds // 60)
        ride_duration_seconds = int(ride_duration_total_seconds % 60)
    else:
        ride_duration_minutes = 0
        ride_duration_seconds = 0

    message = (
        f"Riding for {ride_duration_minutes} minutes and "
        f"{ride_duration_seconds}  seconds. Heart rate: {heart_rate} BPM"
    )

    return html.Span(message)


@app.callback(
    Output("heart-rate-alert", "style"),
    Input("heart-rate-alert-interval", "n_intervals"),
)
def heart_rate_alert(n_intervals: int) -> dict:
    """
    Will display warning message on screen if heart rate is too high or low
    Toggles the display option on the div with id heart-rate-alert
    
    Args:
        n_intervals: A  loop counter. Not used in the function body, but dash requires you to have
        it for the function to be called in repeatedly. 
    """
    current_heart_rate = real_time_processing.current_data.get("heart_rate")
    current_age = real_time_processing.current_data.get("user_age")

    if current_age is None or heart_rate_ok(current_heart_rate, current_age):
        return {"display": "none"}

    return {"display": "block"}


@app.callback(
    Output("heart-rate-alert-description", "children"),
    Input("heart-rate-alert-interval", "n_intervals"),
)
def heart_rate_description(n_intervals: int) -> html.Span:
    """
    Determines output of heart-rate-alert-description
    
    Args:
        n_intervals: A  loop counter. Not used in the function body, but dash requires you to have
        it for the function to be called in repeatedly. 
    """

    current_heart_rate = real_time_processing.current_data.get("heart_rate")
    current_age = real_time_processing.current_data.get("user_age")

    message = "Keep going!"

    if current_heart_rate and current_age:
        if heart_rate_low(current_heart_rate, current_age):
            message = "Heart rate too low, work harder!"
        elif heart_rate_high(current_heart_rate, current_age):
            message = (
                "Heart rate very high! Perhaps take a break or decrease intensity."
            )

    return html.Span(message)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)

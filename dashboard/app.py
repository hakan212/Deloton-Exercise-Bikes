from re import I
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import real_time_processing

app = Dash(__name__, use_pages=False)

app.layout = html.Div([
    html.H1("Deloton Dashboard"),

    #Current Ride info
    html.Div([
        html.H2('Current Ride'),
        html.Div([
            html.H3('Current Rider Account Details'),
            html.Div(id='current-rider-text'),
            dcc.Interval(
                id='current_rider_interval',
                interval=0.5*1000,
                n_intervals=0
            )
        ]),
        html.Div([
            html.H3('Current Ride Stats'),
            html.Div(id='live-ride-text'),
            dcc.Interval(
                id='live-ride-interval',
                interval=0.5*1000, # in milliseconds
                n_intervals=0 #counter for number of refreshes
            )
        ])
    ]),
    #Recent Ride info
    html.Div([
        html.H2('Recent Rides')
    ])
])


@app.callback(Output('current-rider-text', 'children'),
              Input('current_rider_interval', 'n_intervals'))
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
        Height: {data.get('user_height')} cm
        Weight: {data.get('user_weight')} kg"""

    return html.Span(message)

@app.callback(Output('live-ride-text', 'children'),
              Input('live-ride-interval', 'n_intervals'))
def live_ride_details(n_intervals: int) -> html.Span:
    """Returns an html span element containing text with live information on the current ride
    
    Args:
        n_intervals: A  loop counter. Not used in the function body, but dash requires you to have
        it for the function to be called in repeatedly.
    """
    real_time_processing.refresh_data()
    ride_duration_seconds = real_time_processing.current_data.get('duration') or 0
    heart_rate = real_time_processing.current_data.get('heart_rate') or 0
    message = (f'Riding for {int(ride_duration_seconds // 60)} minutes and '
        f'{int(ride_duration_seconds % 60)}  seconds. Heart rate: {heart_rate} BPM')

    return html.Span(message)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
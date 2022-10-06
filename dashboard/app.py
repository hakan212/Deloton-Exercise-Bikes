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
            html.Span('{Placeholder for details...}')
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


@app.callback(Output('live-ride-text', 'children'),
              Input('live-ride-interval', 'n_intervals'))
def live_refresh(n_intervals):
    real_time_processing.refresh_data()

    ride_duration_seconds = real_time_processing.current_data.get('duration') or 0
    heart_rate = real_time_processing.current_data.get('heart_rate') or 0
    
    message = (f'Riding for {ride_duration_seconds // 60} minutes and {ride_duration_seconds % 60} seconds. '
        f'Heart rate: {heart_rate} BPM')
    print(message)

    return html.Span(message)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
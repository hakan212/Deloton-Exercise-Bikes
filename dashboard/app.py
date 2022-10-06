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
                interval=1*1000, # in milliseconds
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
    kafka_message = real_time_processing.c.poll(1) #poll all messages that have occurred since last refresh

    if kafka_message is not None: #ensure we have a message
        log = kafka_message.value().decode('utf-8')

        if 'INFO' in log: #only check for strings with INFO
            real_time_processing.update_current_ride_metrics(real_time_processing.current_data, log)
        
        if 'SYSTEM' in log:
            real_time_processing.update_current_rider_information(real_time_processing.current_data, log)    

        if '-------' in log or 'Getting user data from server' in log:
            real_time_processing.current_data = {}
    
    ride_duration_seconds = real_time_processing.current_data.get('duration') or -1
    heart_rate = real_time_processing.current_data.get('heart_rate') or -1

    message = (f'Riding for {ride_duration_seconds // 60} minutes and {ride_duration_seconds % 60} seconds. '
        f'Heart rate: {heart_rate} BPM')
    return html.Span(message)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
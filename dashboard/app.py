import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


app = Dash(__name__, use_pages=False)

app.layout = html.Div([
    html.H1("Deloton Dashboard"),

    #User info
    html.Div([
        html.Div([
            html.H2('Current Rider Account Details'),
            html.Span('{Placeholder for details...}')
        ]),
        html.Div([
            html.H2('Current Ride Stats'),
            html.Div(id='live-ride-text'),
            dcc.Interval(
                id='live-ride-interval',
                interval=1*1000, # in milliseconds
                n_intervals=0
            )
        ])
    ])
])


@app.callback(Output('live-ride-text', 'children'),
              Input('live-ride-interval', 'n_intervals'))
def live_refresh_placeholder(n_intervals):
    import random
    heart_rate = random.randrange(50, 200)
    return html.Span(
        f'Riding for {n_intervals // 60} minutes and {n_intervals % 60} seconds. Heart rate: {heart_rate} BPM'
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
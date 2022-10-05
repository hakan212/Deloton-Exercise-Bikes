import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


app = Dash(__name__, use_pages=False)

app.layout = html.Div([
    html.H1("Deloton Dashboard"),
    html.Div([
        html.H2('Current Heartrate'),
        html.Div(id='heart-rate-text'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
])


@app.callback(Output('heart-rate-text', 'children'),
              Input('interval-component', 'n_intervals'))
def refresh_heartrate_placeholder(n_intervals):
    import random
    heart_rate = random.randrange(50, 200)
    return html.Span(
        f'Riding for {n_intervals // 60} minutes and {n_intervals % 60} seconds. Heart rate: {heart_rate} BPM'
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
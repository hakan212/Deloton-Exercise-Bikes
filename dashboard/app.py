import dash_bootstrap_components as dbc
from dash import Dash, html


app = Dash(__name__, use_pages=False)

app.layout = html.Div(
    html.H1("Delaton Dashboard")
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)
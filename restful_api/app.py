import json
import os

import pandas as pd
import snowflake.connector as sf
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

USER = os.environ.get("USER")
ACCOUNT = os.environ.get("ACCOUNT")
PASSWORD = os.environ.get("PASSWORD")
WAREHOUSE = os.environ.get("WAREHOUSE")
DATABASE = os.environ.get("DATABASE")
SCHEMA = os.environ.get("SCHEMA")

flask_app = Flask(__name__)

# Snowflake connection

conn = sf.connect(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA,
)

def run_query(conn, query):
    """Runs a SQL query in Snowflake data warehouse

    Args:
        conn: Snowflake DB connection
        query: SQL query

    Returns:
        query_results: data associated with the query made
    """
    cs = conn.cursor()
    cs.execute(query)
    query_results = cs.fetchall()
    cs.close()
    return query_results


# API Endpoints

# GET Endpoints
@flask_app.route('/')
def default():
    return "Delaton Exercise Bikes API"

@flask_app.route("/rider/<rider_id>", method=["GET"])
def get_rider_id(rider_id);
    snow_sql = request.args.get

@flask_app.route("/rider/<rider_id>/rides", method=["GET"])


@flask_app.route("/daily", method=["GET"])
#daily endpoint should handle both daily and daily + query string


# DELETE Endpoints
@flask_app.route("/ride/<ride_id>", method=["DELETE"])
def delete_ride_id(ride_id):


if __name__ == "__main__":
    flask_app.run()

import json
import os

import pandas as pd
import sqlalchemy
import snowflake.connector as sf
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

USER = os.environ.get("USER")
ACCOUNT = os.environ.get("ACCOUNT")
PASSWORD = os.environ.get("PASSWORD")
WAREHOUSE = os.environ.get("WAREHOUSE")
DATABASE = os.environ.get("DATABASE")
SCHEMA = os.environ.get("SCHEMA") # need to change to the correct table

flask_app = Flask(__name__)

# Snowflake-SQLalchemy connection

engine = create_engine(URL(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA
))

connection = engine.connect()


def run_query(query, engine=engine):
    """Runs a SQL query in Snowflake data warehouse

    Args:
        conn: Snowflake_SQLalchemy DB connection
        query: SQL query

    Returns:
        query_results: data associated with the query made
    """
    conn = engine.connect()

    try: 
        query_results = conn.execute(query)
    finally:
        connection.close()
 
    data = query_results.fetchall()
    
    return data


# API Endpoints

# GET Endpoints
@flask_app.route('/')
def default():
    return "Delaton Exercise Bikes API"

@flask_app.route("/ride/<ride_id>")
def get_ride(ride_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE id = {ride_id}
    """
    ride = run_query(query)

    response = jsonify({"status": 200,"ride": ride})

    return response


@flask_app.route("/rider/<rider_id>", method=["GET"])
def get_rider(rider_id):
    query = f"""
        SELECT *
            FROM riders
            WHERE id = {rider_id}
    """
    rider = run_query(query)

    response = jsonify({"status": 200,"rider": rider})

    return response


@flask_app.route("/rider/<rider_id>/rides", method=["GET"])
def get_rides_for_rider(rider_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE rider_id = {rider_id}
    """
    rides = run_query(query)

    response = jsonify({"status": 200,"rides": rides})

    return response


@flask_app.route("/daily", method=["GET"])
#daily endpoint should handle both daily and daily + query string


# DELETE Endpoints
@flask_app.route("/ride/<ride_id>", method=["DELETE"])
def delete_ride_id(ride_id):


if __name__ == "__main__":
    flask_app.run(debug=True)

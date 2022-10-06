import os
from datetime import datetime, timedelta
import json
import snowflake.connector as sf
import time
from dotenv import load_dotenv
from flask import Flask, jsonify, request


load_dotenv()

USER = os.environ.get("USER")
ACCOUNT = os.environ.get("ACCOUNT")
PASSWORD = os.environ.get("PASSWORD")
WAREHOUSE = os.environ.get("WAREHOUSE")
DATABASE = os.environ.get("DATABASE")
BATCH_SCHEMA = os.environ.get("BATCH_SCHEMA") # now the name of the batch production schema

flask_app = Flask(__name__)

# Snowflake-SQLalchemy connection
conn = sf.connect(
        user="admin",
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=BATCH_SCHEMA
)

def run_query(query, conn):
    """Runs a SQL query in Snowflake data warehouse

    Args:
        conn: Snowflake_SQLalchemy DB connection
        query: SQL query

    Returns:
        query_results: data associated with the query made
    """
    cursor = conn.cursor()

    query_results = cursor.execute(query)
   
    return query_results


# API Endpoints

# GET Endpoints
@flask_app.route("/")
def default():
    return "Delaton Exercise Bikes API"


@flask_app.route("/rides", methods=["GET"])
def get_rides():
    query = f"""
        SELECT *
            FROM rides
    """
    query_results = run_query(query, conn)

    json_string = query_results.fetch_pandas_all().to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


@flask_app.route("/rides/<ride_id>", methods=["GET"])
def get_ride(ride_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE ride_id = {ride_id}
    """
    query_results = run_query(query, conn)

    json_string = query_results.fetch_pandas_all().to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "ride": parsed_json})

    return response


@flask_app.route("/rider/<rider_id>", methods=["GET"])
def get_rider(rider_id):
    query = f"""
        SELECT *
            FROM users
            WHERE user_id = {rider_id}
    """
    query_results = run_query(query, conn)

    json_string = query_results.fetch_pandas_all().to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rider": parsed_json})

    return response


@flask_app.route("/rider/<rider_id>/rides", methods=["GET"])
def get_rides_for_rider(rider_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE user_id = {rider_id}
    """
    query_results = run_query(query, conn)

    json_string = query_results.fetch_pandas_all().to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


@flask_app.route("/daily", methods=["GET"])
# daily endpoint should handle both daily and daily + query string
def get_daily():
    requested_date = request.args.get("date")

    if requested_date is not None:
        
        query = f"""
            SELECT *
                FROM rides
                WHERE TO_DATE(begin_timestamp) = TO_DATE('{requested_date}')
        """
        query_results = run_query(query, conn)

        json_string = query_results.fetch_pandas_all().to_json(orient="records")

        parsed_json = json.loads(json_string)

        if len(parsed_json) == 0:
            response = jsonify({"status": 204, "rides": "No content"})

            return response

        response = jsonify({"status": 200, "rides": parsed_json})

        return response

    query = f"""
        SELECT *
            FROM rides
            WHERE TO_DATE(begin_timestamp) = TO_DATE(CURRENT_DATE)
        """
    query_results = run_query(query, conn)

    json_string = query_results.fetch_pandas_all().to_json(orient="records")

    parsed_json = json.loads(json_string)

    if len(parsed_json) == 0:
            response = jsonify({"status": 204, "rides": "No content"})

            return response

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


# DELETE Endpoints
@flask_app.route("/ride/<ride_id>", methods=["POST"])
def delete_ride_id(ride_id):
    query = f"""
        DELETE FROM rides
            WHERE id = {ride_id}
    """
    run_query(query)

    response = jsonify({"status": 200})

    return response


if __name__ == "__main__":
    # TODO: import waitress for when we containerize
    flask_app.run(debug=True)

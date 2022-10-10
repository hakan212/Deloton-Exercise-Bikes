import json
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
MART_SCHEMA = os.getenv("MART_SCHEMA")
PRODUCTION_SCHEMA = os.getenv("PRODUCTION_SCHEMA")

flask_app = Flask(__name__)


def get_engine_connection():
    """
    Connects to postgreSQL DBMS on AWS Aurora

    """
    conn_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(conn_string)


def run_query(query):
    """Runs a SQL query in AWS Aurora RDBMS

    Args:
        query: SQL query

    Returns:
        query_results: data associated with the query made
    """
    engine = get_engine_connection()

    query_results = engine.execute(query)

    return query_results


# API Endpoints

# GET Endpoints
@flask_app.route("/")
def default():
    return "Deloton Exercise Bikes API"


@flask_app.route("/rides", methods=["GET"])
def get_rides():
    query = f"""
        SELECT *
            FROM zookeepers_production.rides
    """
    query_results = run_query(query)

    json_string = pd.read_sql_table('rides',)      .to_json(orient="records")

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
    query_results = run_query(query)

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
    query_results = run_query(query)

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
    query_results = run_query(query)

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
        query_results = run_query(query)

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
    query_results = run_query(query)

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

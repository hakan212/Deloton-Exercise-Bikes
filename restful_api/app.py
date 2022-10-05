import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

load_dotenv()

USER = os.environ.get("USER")
ACCOUNT = os.environ.get("ACCOUNT")
PASSWORD = os.environ.get("PASSWORD")
WAREHOUSE = os.environ.get("WAREHOUSE")
DATABASE = os.environ.get("DATABASE")
SCHEMA = os.environ.get("SCHEMA")  # need to change to the correct table

flask_app = Flask(__name__)

# Snowflake-SQLalchemy connection


def run_query(query, db_engine=engine):
    """Runs a SQL query in Snowflake data warehouse

    Args:
        conn: Snowflake_SQLalchemy DB connection
        query: SQL query

    Returns:
        query_results: data associated with the query made
    """
    engine = create_engine(
        URL(
            user=USER,
            password=PASSWORD,
            account=ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema=SCHEMA,
        )
    )

    conn = db_engine.connect()

    try:
        query_results = conn.execute(query)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        conn.close()
        engine.dispose()

    data = query_results.fetchall()

    return data


# API Endpoints

# GET Endpoints
@flask_app.route("/")
def default():
    return "Delaton Exercise Bikes API"


@flask_app.route("/ride/<ride_id>", method=["GET"])
def get_ride(ride_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE id = {ride_id}
    """
    ride = run_query(query)

    response = jsonify({"status": 200, "ride": ride})

    return response


@flask_app.route("/rider/<rider_id>", method=["GET"])
def get_rider(rider_id):
    query = f"""
        SELECT *
            FROM riders
            WHERE id = {rider_id}
    """
    rider = run_query(query)

    response = jsonify({"status": 200, "rider": rider})

    return response


@flask_app.route("/rider/<rider_id>/rides", method=["GET"])
def get_rides_for_rider(rider_id):
    query = f"""
        SELECT *
            FROM rides
            WHERE rider_id = {rider_id}
    """
    rides = run_query(query)

    response = jsonify({"status": 200, "rides": rides})

    return response


@flask_app.route("/daily", method=["GET"])
# daily endpoint should handle both daily and daily + query string
def get_daily():
    requested_date = request.args.get("date")

    if requested_date is not None:
        query = f"""
            SELECT *
                FROM rides
                WHERE begin_timestamp = {requested_date}
        """
        requested_date_rides = run_query(query)

        response = jsonify({"status": 200, "rides": requested_date_rides})

        return response

    query = f"""
        SELECT *
            FROM rides
            WHERE begin_timestamp > {datetime.now() - timedelta(days=1)}
        """
    daily_rides = run_query(query)

    response = jsonify({"status": 200, "rides": daily_rides})

    return response


# DELETE Endpoints
@flask_app.route("/ride/<ride_id>", method=["POST"])
# Seems like DELETE requests aren't supported - workaround with POST for now
def delete_ride_id(ride_id):
    query = f"""
        DELETE FROM rides
            WHERE id = {ride_id}
    """
    run_query(query)

    second_query = f"""
        SELECT *
            FROM rides
            WHERE id = {ride_id}
    """
    ride = run_query(second_query)

    response = jsonify({"status": 204, "ride": ride})

    return response


if __name__ == "__main__":
    # TODO: import waitress for when we containerize
    flask_app.run(debug=True)

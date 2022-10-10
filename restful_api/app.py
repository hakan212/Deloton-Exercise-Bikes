import json
import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from assets.api_engine_wrapper import database_connection

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


flask_app = Flask(__name__)


def create_connection():
    """Creates an instance of database_connection, which is used as an engine wrapper
    
    Returns:
        database_connection object
    """

    conn = database_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

    return conn


conn = create_connection()

# API Endpoints

## GET Endpoints


@flask_app.route("/")
def default():
    return "Deloton Exercise Bikes API"


@flask_app.route("/rides", methods=["GET"])
def get_rides():

    json_string = conn.read_table_into_df(table="rides").to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


@flask_app.route("/rides/<ride_id>", methods=["GET"])
def get_ride(ride_id):

    json_string = conn.select_ride(ride_id).to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "ride": parsed_json})

    return response


@flask_app.route("/rider/<rider_id>", methods=["GET"])
def get_rider(rider_id):

    json_string = conn.select_user(rider_id).to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rider": parsed_json})

    return response


@flask_app.route("/rider/<rider_id>/rides", methods=["GET"])
def get_rides_for_rider(rider_id):

    json_string = conn.select_rides_with_user(rider_id).to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


@flask_app.route("/daily", methods=["GET"])
# daily endpoint should handle both daily and daily + query string
def get_daily():
    requested_date = request.args.get("date")

    if requested_date is None:
        requested_date = date.today().strftime("%Y-%m-%d")

    json_string = conn.select_rides_with_date(requested_date).to_json(orient="records")

    parsed_json = json.loads(json_string)

    if len(parsed_json) == 0:
        response = jsonify({"status": 204, "rides": "No content"})

        return response

    response = jsonify({"status": 200, "rides": parsed_json})

    return response


## DELETE Endpoints
@flask_app.route("/ride/<ride_id>", methods=["DELETE"])
def delete_ride_id(ride_id):
    conn.delete_ride(ride_id)

    response = jsonify({"status": 200})

    return response


if __name__ == "__main__":
    flask_app.run(debug=True)

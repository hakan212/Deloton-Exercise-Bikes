import json
import os
from datetime import date
from pickle import TRUE
from unittest import result

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from assets.api_engine_wrapper import databaseConnection

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
        databaseConnection object
    """

    conn = databaseConnection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

    return conn


conn = create_connection()

# API Endpoints

## GET Endpoints


@flask_app.route("/")
def default():
    content1 = "Deleton Exercise Bikes API <br/> Append these endpoints to make your request: <br/> "
    content2 = "<b>/rides:</b> Query all rides in the database <br/> <b>/rides/ride_id:</b> Query a specific ride with a ride_id <br/>"
    content3 = "<b>/user/user_id:</b> Query a specific user with a user_id <br/> <b>/user/user_id/rides:</b> Obtain all rides for a specific user<br/>"
    content4 = "<b>/daily?date=YYYY-MM-DD:</b> Obtain all rides that have happened on a specific date. Leave the date argument blank to use today's date<br/>"
    content5 = "<b>/rides/ride_id method=DELETE</b>: Sending a delete request for a specific ride id will delete the ride<br/>"
    content6 = "<b>/user/user_id method=DELETE</b>: Sending a delete request for a specific user id will delete the user and all rides they have been on<br/>"
    return content1 + content2 + content3 + content4 + content5 + content6


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


@flask_app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):

    json_string = conn.select_user(user_id).to_json(orient="records")

    parsed_json = json.loads(json_string)

    response = jsonify({"status": 200, "user": parsed_json})

    return response


@flask_app.route("/user/<user_id>/rides", methods=["GET"])
def get_rides_for_user(user_id):

    json_string = conn.select_rides_with_user(user_id).to_json(orient="records")

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
@flask_app.route("/rides/<ride_id>", methods=["DELETE"])
def delete_ride_id(ride_id):
    result = conn.delete_ride(ride_id)

    response = jsonify({"status": result})

    return response


@flask_app.route("/user/<user_id>", methods=["DELETE"])
def delete_user_id(user_id):
    result = conn.delete_user(user_id)

    response = jsonify({"status": result})

    return response


if __name__ == "__main__":
    flask_app.run(debug=True,host='0.0.0.0',port=5001)

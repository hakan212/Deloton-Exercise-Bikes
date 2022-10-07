import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


SCHEMA_NAME = os.getenv('SCHEMA_NAME')
load_dotenv()

class database_connection:
    def __init__(
        self,
        database_name,
        user,
        password,
        host,
        port,
    ):
        self.engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{database_name}"
        )

    def read_table_into_df(self, schema, table):
        """Read table into pandas dataframe from chosen schema"""
        df = pd.read_sql_table(table, con=self.engine, schema=schema)
        return df

    def select_user(self, user_dictionary):
        """Queries user table to obtain rows with user, used to check if user is new"""

        select_user_query = f"""
        select user_id from {SCHEMA_NAME}.users
        where user_id = (%s)"""  # parameterised query avoids sql injection

        user_df = pd.read_sql(
            select_user_query, con=self.engine, params=[user_dictionary["user_id"]]
        )

        return user_df

    def insert_users_query(self, user_dictionary):
        """Insert new user into users table"""

        with self.engine.connect() as connection:  # Connection automatically closes at end of code block

            insert_users_query = f"""
            INSERT INTO {SCHEMA_NAME}.users(user_id, first_name, last_name, gender, date_of_birth, 
            height_cm, weight_kg, house_name, street, region, postcode, email, account_created)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""

            parameterised_values = (
                user_dictionary["user_id"],
                user_dictionary["first_name"],
                user_dictionary["last_name"],
                user_dictionary["gender"],
                user_dictionary["date_of_birth"],
                user_dictionary["height_cm"],
                user_dictionary["weight_kg"],
                user_dictionary["house_number"],
                user_dictionary["street_name"],
                user_dictionary["region"],
                user_dictionary["postcode"],
                user_dictionary["email_address"],
                user_dictionary["account_create_date"],
            )

            connection.execute(insert_users_query, parameterised_values)

    def insert_rides_query(
        self,
        user_dictionary,
        begin_timestamp,
        duration,
        total_power,
        mean_power,
        mean_resistance,
        mean_rpm,
        mean_heart_rate,
    ):
        """Insert new rides into rides table"""
        with self.engine.connect() as connection:
            insert_rides_query = f"""
            INSERT INTO {SCHEMA_NAME}.rides(user_id, begin_timestamp, total_duration_sec, 
            total_power, mean_power, mean_resistance, mean_rpm, mean_heart_rate)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"""

            parameterised_values = (
                user_dictionary["user_id"],
                begin_timestamp,
                duration,
                total_power,
                mean_power,
                mean_resistance,
                mean_rpm,
                mean_heart_rate,
            )

            connection.execute(insert_rides_query, parameterised_values)

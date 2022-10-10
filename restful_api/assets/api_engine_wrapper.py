import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

SCHEMA_NAME = os.getenv("SCHEMA_NAME")
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

    def read_table_into_df(self, table, schema=SCHEMA_NAME):
        """Read a whole table into a pandas dataframe"""
        df = pd.read_sql_table(table, con=self.engine, schema=schema)
        return df

    def select_ride(self, ride_id):
        """Queries rides table to obtain specific ride"""

        select_ride_query = f"""
        select * from {SCHEMA_NAME}.rides
        where ride_id = (%s)"""  # parameterised query avoids sql injection

        ride_df = pd.read_sql(select_ride_query, con=self.engine, params=[ride_id])

        return ride_df

    def select_user(self, user_id):
        """Queries user table to obtain specific user"""

        select_user_query = f"""
        select * from {SCHEMA_NAME}.users
        where user_id = (%s)"""

        user_df = pd.read_sql(select_user_query, con=self.engine, params=[user_id])

        return user_df

    def select_rides_with_user(self, user_id):
        """Queries ride table to obtain rides for a specific user"""

        select_rides_query = f"""
        select * from {SCHEMA_NAME}.rides
        where user_id = (%s)"""

        ride_df = pd.read_sql(select_rides_query, con=self.engine, params=[user_id])

        return ride_df

    def select_rides_with_date(self, date):
        """Queries ride table to obtain rides on a given date"""
        select_rides_query = f"""
            SELECT *
                FROM {SCHEMA_NAME}.rides
                WHERE TO_CHAR(begin_timestamp,'YYYY-MM-DD') = (%s)
        """

        rides_df = pd.read_sql(select_rides_query, con=self.engine, params=[date])

        return rides_df

    def delete_ride(self, ride_id):
        """Deletes ride with a specific ride_id"""
        delete_ride_query = f"""
            DELETE 
                FROM {SCHEMA_NAME}.rides
                WHERE ride_id = (%s)
        """
        with self.engine.connect() as connection:
            connection.execute(delete_ride_query, (ride_id))

    def delete_user(self, user_id):
        """Deletes user with a specific user_id, along with all rides they have been on"""
        delete_rides_query = f"""
            DELETE 
                FROM {SCHEMA_NAME}.rides
                WHERE user_id = (%s)
        """

        delete_user_query = f"""
            DELETE 
                FROM {SCHEMA_NAME}.users
                WHERE user_id = (%s)
        """

        with self.engine.connect() as connection:
            connection.execute(delete_rides_query, (user_id))
            connection.execute(delete_user_query, (user_id))

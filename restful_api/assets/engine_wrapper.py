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

    def read_table_into_df(self, table, schema=SCHEMA_NAME):
        """Read table into pandas dataframe from chosen schema"""
        df = pd.read_sql_table(table, con=self.engine, schema=schema)
        return df


    def select_ride(self, ride_id):
        """Queries ride table to obtain specific ride"""

        select_ride_query = f"""
        select * from {SCHEMA_NAME}.rides
        where ride_id = (%s)"""  # parameterised query avoids sql injection

        ride_df = pd.read_sql(
            select_ride_query, con=self.engine, params=[ride_id]
        )

        return ride_df

    def select_user(self, user_id):
        """Queries user table to obtain specific user"""

        select_user_query = f"""
        select * from {SCHEMA_NAME}.users
        where user_id = (%s)"""  # parameterised query avoids sql injection

        user_df = pd.read_sql(
            select_user_query, con=self.engine, params=[user_id]
        )

        return user_df




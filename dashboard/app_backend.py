import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.environ.get('USER')
ACCOUNT = os.environ.get('ACCOUNT')
PASSWORD = os.environ.get('PASSWORD')
WAREHOUSE= os.environ.get('WAREHOUSE')
DATABASE= os.environ.get('DATABASE')
SCHEMA= os.environ.get('SCHEMA')


cursor_type = snowflake.connector.cursor.SnowflakeCursor

def connect_to_snowflake() -> cursor_type:
    """Connect to the snowflake schema and obtain a cursor"""
    conn = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA
    )

    cs = conn.cursor()
    return cs


def query_snowflake_into_df(cs: cursor_type) -> pd.Dataframe:
    """Query recent_rides table and obtain a pandas dataframe of data"""
    snowflake_df = cs.execute('SELECT * FROM recent_rides').fetch_pandas_all()

    return snowflake_df




# TODO: query data into a pandas dataframe and pickle (12hr requirement)
# should boost performance
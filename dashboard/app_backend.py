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

conn = snowflake.connector.connect(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA
)
cs = conn.cursor()
cursor_type = type(cs)

def query_snowflake_into_df(cs: cursor_type) -> pd.Dataframe:
    snowflake_df = cs.execute('SELECT * FROM recent_rides').fetch_pandas_all()

    return snowflake_df




# TODO: query data into a pandas dataframe and pickle (12hr requirement)
# should boost performance
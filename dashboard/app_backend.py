import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: decide on the schema to read from in snowflake (data mart)

# Snowflake Connection

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
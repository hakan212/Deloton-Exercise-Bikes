import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine,inspect

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
MART_SCHEMA = os.getenv("MART_SCHEMA")
PRODUCTION_SCHEMA = os.getenv("PRODUCTION_SCHEMA")


if __name__ == "__main__":
    pass
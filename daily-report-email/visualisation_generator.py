import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
PRODUCTION_SCHEMA = 'zookeepers_production'

pd.options.plotting.backend = "plotly"


def get_engine_connection():
        """Connects to postgreSQL DBMS on AWS Aurora

        Returns:
            DB engine
        """
        conn_string = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        return create_engine(conn_string)


def get_dataframe():  
    """
    Creates a Pandas DataFrame by querying
    AWS Aurora with an SQL statement.

    Data collected is rides and users joined
    where the timestamp is within the last 24
    hours.
    """

    query = f"""
        WITH user_gender_dob AS (
            SELECT user_id, gender,
                DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))
                    AS age 
                FROM {PRODUCTION_SCHEMA}.users
        ),

        rides_before AS (
            SELECT *
                FROM {PRODUCTION_SCHEMA}.rides
                WHERE begin_timestamp > (CURRENT_DATE) and begin_timestamp < (CURRENT_DATE + 1)
        )

        SELECT ugd.user_id, rb.ride_id, ugd.gender, ugd.age, rb.begin_timestamp,
            rb.total_duration_sec, rb.total_power, rb.mean_power, rb.mean_resistance,
                rb.mean_rpm, rb.mean_heart_rate

            FROM user_gender_dob AS ugd
            RIGHT JOIN rides_before AS rb
                ON ugd.user_id = rb.user_id
    """

    df = pd.read_sql(query, con=get_engine_connection())

    return df

def get_number_of_rides(df):
    """
    Return the total number of
    rides in df_rides
    """
    return len(df)

def get_gender_rides_pie(df):
    gender_df = df['gender'].value_counts()
    gender_df.values
    gender_fig = px.pie(gender_df,values=gender_df.values,names=gender_df.index,title=f'Gender of bicycle users for {date.today()}',width=500,height=500)
    return gender_fig

def get_age_rides_segments(df):
    age_bin = [0,15,30,45,60,75,90,105]
    age_df = df['age'].value_counts(bins=age_bin,sort=False)
    age_range_list = ['0-15','15-30','30-45','45-60','60-75','75-90','90-105+']

    age_bin_ticks = age_df.index.astype(str)
    age_fig = px.bar(x=age_bin_ticks, y=age_df.values,labels={'y':'Number of riders','x':'Age ranges of riders'},width=750,title=f'Age ranges of bicycle riders for {date.today()}')
    age_fig.update_xaxes(tickvals=age_bin_ticks, ticktext = age_range_list)

    return age_fig

def get_mean_total_power(df):
    mean_total_power = int(df['total_power'].mean())
    return mean_total_power

def get_mean_power_output(df):
    mean_power_output = df['mean_power'].mean().round(2)
    return mean_power_output

def get_mean_heart_rate(df):
    mean_heart_rate = df['mean_heart_rate'].mean().round(1)
    return mean_heart_rate

    
if __name__ == "__main__":
    df_rides = get_dataframe()
    num_rides = get_number_of_rides(df_rides)


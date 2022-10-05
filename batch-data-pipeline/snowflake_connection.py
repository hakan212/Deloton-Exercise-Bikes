import os

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

USER = os.environ.get('USER')
ACCOUNT = os.environ.get('ACCOUNT')
PASSWORD = os.environ.get('PASSWORD')
WAREHOUSE= os.environ.get('WAREHOUSE')
DATABASE= os.environ.get('DATABASE')
SCHEMA= os.environ.get('SCHEMA')


def connect_to_snowflake():
    """connect to snowflake to make queries"""
    print(USER)
    conn = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema='ZOOKEEPERS_BATCH_PRODUCTION'
    )
    cs = conn.cursor()
    return cs

 
def insert_into_users(cs,user_dictionary):
    """Makes insert query into users table once all relevant information has been obtained"""
    cs.execute(
                """INSERT INTO users(user_id, first_name, last_name, gender, date_of_birth, 
                height_cm, weight_kg, house_name, street, region, postcode, email, account_created) """
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                user_dictionary['user_id'],user_dictionary['first_name'],user_dictionary['last_name'],user_dictionary['gender'],
                user_dictionary['date_of_birth'],user_dictionary['height_cm'],user_dictionary['weight_kg'],user_dictionary['house_number'],
                user_dictionary['street_name'],user_dictionary['region'],user_dictionary['postcode'],
                user_dictionary['email_address'],user_dictionary['account_create_date']
                )
                )
    print('made insert into users')

 
def insert_into_rides(cs, user_dictionary, begin_timestamp, duration, total_power,
                mean_power, mean_resistance, mean_rpm, mean_heart_rate):
    """Makes insert query into rides table once all relevant information has been obtained"""
    cs.execute(
                "INSERT INTO rides(user_id, begin_timestamp, total_duration_sec, total_power, mean_power, mean_resistance, mean_rpm, mean_heart_rate) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (user_dictionary['user_id'], begin_timestamp, duration, 
                total_power, mean_power, mean_resistance, 
                mean_rpm, mean_heart_rate)
                
                )
    print('made insert into rides')
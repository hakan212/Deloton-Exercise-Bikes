def handler(event, context):
    import os

    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    load_dotenv()

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    MART_SCHEMA = os.getenv("MART_SCHEMA")
    PRODUCTION_SCHEMA = os.getenv("PRODUCTION_SCHEMA")

    def get_engine_connection():
        """
        Connects to postgreSQL DBMS on AWS Aurora
        """
        conn_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        return create_engine(conn_string)

    def run_query(query):
        """
        Runs a SQL query in AWS Aurora RDBMS

        """
        engine = get_engine_connection()

        query_results = engine.execute(query)

        return query_results

    def transfer_production_to_mart():
        """
        Summary: queries users and rides table in the production
        schema.

        Using two CTEs to only get data that is 12 hours
        fresh.

        The two CTEs are right joined to make up the required
        data for the recent_rides tables in the mart schema
        """

        query = f"""      
            INSERT INTO {MART_SCHEMA}.recent_rides
            
            WITH user_gender_dob AS (
                SELECT user_id, gender,
                    DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))
                        AS age 
                    FROM {PRODUCTION_SCHEMA}.users
            ),
            rides_before AS (
                SELECT *
                    FROM {PRODUCTION_SCHEMA}.rides
                    WHERE begin_timestamp > (CURRENT_DATE - INTERVAL '12 hours')
            )
            SELECT ugd.user_id, rb.ride_id, ugd.gender, ugd.age, rb.begin_timestamp,
                rb.total_duration_sec, rb.total_power, rb.mean_power, rb.mean_resistance,
                    rb.mean_rpm, rb.mean_heart_rate

                FROM user_gender_dob AS ugd
                RIGHT JOIN rides_before AS rb
                    ON ugd.user_id = rb.user_id
        """

        run_query(query)

        print("transferred data from production to schema")

    def clear_stale_data():
        """
        Executes a delete query on the recent_rides
        table in the mart.

        Data older than 12 hours ago will be deleted from the table.
        """

        query = f"""
            DELETE FROM {MART_SCHEMA}.recent_rides
                WHERE begin_timestamp < (CURRENT_DATE - INTERVAL '12 hours')
        """

        run_query(query)

        print("dropped rows older than 12 hours")

    transfer_production_to_mart()
    clear_stale_data()

    return "Function Executed"

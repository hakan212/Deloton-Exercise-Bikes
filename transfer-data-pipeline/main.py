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
        conn_string = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        return create_engine(conn_string)


    def transfer_production_to_mart():
        """
        Summary: queries users and rides table in the production
        schema.

        Using two CTEs to only get data that is 12 hours
        fresh.

        The two CTEs are right joined to make up the required
        data for the recent_rides tables in the mart schema

        """
        with get_engine_connection() as conn:

            query = f"""
                INSERT INTO {MART_SCHEMA}.recent_rides

                WITH recent_rides_data AS(

                    WITH user_gender_dob AS (
                    SELECT user_id, gender,
                        DATEDIFF(hour,date_of_birth, CURRENT_DATE)/8766 AS age
                        FROM {PRODUCTION_SCHEMA}.users
                    ),

                    rides_before AS (
                        SELECT *
                            FROM {PRODUCTION_SCHEMA}.rides
                            WHERE TO_DATE(rs.begin_timestamp) > DATEADD(HOUR, -12, CURRENT_DATE)
                    )

                    SELECT ugd.*, rb.*
                        FROM user_gender_dob AS ugd
                        RIGHT JOIN rides_before AS rb
                            ON ugd.user_id = rb.user_id
                )

                SELECT * FROM recent_rides_data;
            """

            conn.execute(query)

        print("transferred data from production to schema")


    def clear_stale_data():
        """
        Executes a delete query on the recent_rides
        table in the mart.

        Data older than 12 hours ago will be deleted from the table.
        """
        with get_engine_connection() as conn:

            query = f"""
                DELETE FROM {MART_SCHEMA}.recent_rides
                    WHERE TO_DATE(begin_timestamp) < DATEADD(HOUR, -12, CURRENT_DATE)
            """

            conn.execute(query)

        print("dropped rows older than 12 hours")


    if __name__ == "__main__":
        transfer_production_to_mart()
        clear_stale_data()

    return "Function Executed"


import pandas as pd
from sqlalchemy import create_engine

class database_connection: 
    def __init__(
        self,
        database_name,
        user,
        password,
        host,
        port,
    ): 
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
    
    
    def read_table(self,schema,table): 
        """Read table from chosen schema"""
        df = pd.read_sql_table(table,con=self.engine,schema=schema)
        return df
    
    def insert_table(self,schema,table,user_dictionary):
        """Insert data into chosen table"""
        
        with self.engine.connect() as connection:

            insert_users_query = """INSERT INTO users(user_id, first_name, last_name, gender, date_of_birth, 
                    height_cm, weight_kg, house_name, street, region, postcode, email, account_created)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""

            tuple_of_values = (
                user_dictionary["user_id"],
                user_dictionary["first_name"],
                user_dictionary["last_name"],
                user_dictionary["gender"],
                user_dictionary["date_of_birth"],
                user_dictionary["height_cm"],
                user_dictionary["weight_kg"],
                user_dictionary["house_number"],
                user_dictionary["street_name"],
                user_dictionary["region"],
                user_dictionary["postcode"],
                user_dictionary["email_address"],
                user_dictionary["account_create_date"],
            )

            connection.execute(insert_users_query,tuple_of_values)
        
        



    

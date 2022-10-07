
import pandas as pd
from sqlalchemy import create_engine

from ingestion.ingestion_load_s3 import load_s3_data


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
    
    
    def read_table(self,schema='week4_hakan_staging',table='staging_ecommerce'): #All functions go to staging database by default
        """Read table from chosen schema"""
        staging_df = pd.read_sql_table(table,con=self.engine,schema=schema)
        return staging_df
        
        
    def drop_table(self,schema='week4_hakan_staging',table='staging_ecommerce'):
        """Drop table from chosen schema"""
        with self.engine.connect() as connection:

            drop_table_query = f'''DROP TABLE IF EXISTS {schema}.{table}'''
            connection.execute(drop_table_query)
            print('Table dropped')


    def load_df_to_database(self,schema='week4_hakan_staging', table='staging_ecommerce', col_name='Order Number', df=load_s3_data()):
        """Load dataframe into chosen database"""
        try:
            existing_df = pd.read_sql_table(table,con=self.engine,schema=schema)
            exclude_existing_data = (~df[col_name].isin(existing_df[col_name])) #Exclude existing data to avoid repeated data
            df = df[exclude_existing_data] 

        except ValueError as e:
            print(e,f'There were no duplicates to be checked as the {table} in {schema} does not exist')

        finally:
            df.to_sql(table, con=self.engine,schema=schema,index=False,if_exists='append') #Append data to build the dataset rather than replacing old data
            print('combined df loaded into database')
    

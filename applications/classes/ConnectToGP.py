import getpass
from sqlalchemy import create_engine
from sqlalchemy import text
import polars as pl
import streamlit as st
import psycopg2
import pandas as pd
import os

class ConnectToGP:

    def __init__(self, host: str, database: str, statement_timeout: int):
        self.username = getpass.getuser().split('_')[0]
        self.conn = create_engine(f'postgresql+psycopg2://{self.username}@{host}/{database}'
                                  , pool_timeout=10
                                  , isolation_level='AUTOCOMMIT'
                                  , max_overflow=0
                                  , execution_options={"postgresql_readonly": True}
                                  , connect_args={"connect_timeout": 30,
                                                  "options": f"-c statement_timeout={statement_timeout}"})
        self.conn_uri = f'postgresql+psycopg2://{self.username}@{host}/{database}'

    def execute_sql_pd(self, query: str) -> "pd.DataFrame":
        return pd.read_sql(query, self.conn)

    def execute_sql_text(self, query: str) -> "cursor":
        cursor = self.conn.connect()
        result = cursor.execute(text(query))
        cursor.close()
        return result

    def execute_sql_pl(self, query: str) -> "pl.DataFrame":
        return pl.read_database(query=query, connection=self.conn.connect())

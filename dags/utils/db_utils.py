import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    dbname=os.getenv("POSTGRES_DB_STOCK")
    user=os.getenv("POSTGRES_USER")
    password=os.getenv("POSTGRES_PASSWORD")
    host=os.getenv("POSTGRES_HOST")
    port=os.getenv("POSTGRES_PORT", "5432")
    print(dbname, user, password, host, port)
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn
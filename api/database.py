import os
import psycopg
from dotenv import load_dotenv

# dot env
load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. Please create a .env file."
    )


def get_db_connection():
    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
        # In a real app, you might log this error more formally
        raise

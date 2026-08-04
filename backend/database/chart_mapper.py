import os
import psycopg
import json
from psycopg.rows import dict_row
from fastapi import FastAPI

# Initialize API
app = FastAPI()

@app.get("/chart-data")
def fetch_all_data():

    # Get database url that vercel will bring to access database
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise KeyError("DATABASE_URL is not set in your environment variables!")

    # Connect to database
    with psycopg.connect(db_url, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM historical_car_listing")
            rows = cursor.fetchall()
            json.dumps(rows, indent=4) # Converts to JSON format
            return rows
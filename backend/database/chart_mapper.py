import os
import psycopg
from psycopg.rows import dict_row
from decimal import Decimal

def fetch_all_data():
    # Get database url that render will bring to access database
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        raise KeyError("DATABASE_URL is not set in your environment variables!")

    # Connect to database
    with psycopg.connect(db_url, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM historical_car_listing")
            rows = cursor.fetchall()
            
            # Convert Decimal to float so FastAPI can JSON-serialize it
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        row[key] = float(value)
            
            return rows
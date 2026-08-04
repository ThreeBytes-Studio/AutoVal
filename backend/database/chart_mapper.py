import os
import psycopg

# Fetch data from database
def fetch_data():

    # Get database url that vercel will bring to access database
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise KeyError("DATABASE_URL is not set in your environment variables!")

    # Connect to database
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM historical_car_listing")
            rows = cursor.fetchall()
            # TODO: Kay Chyrus to, [optional] add JSON friendly format
            return rows

# TODO: Princess, ikaw sa implementation ng fastAPI, gamitin mo yung fetch_data function ko dahil eto yung kukuha ng mga datas from database, gagawin mo ay apply mo yung FastAPI dito na kung saan makukuha mo yung datas from fetch_data and mapaparse mo sa website. 

# [Optional]: Di ko parin gaanong gets yung FastAPI so aaralin ko pa, pero feel free to send review request para double check ko
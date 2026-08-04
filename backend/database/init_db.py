import os
import psycopg
from pathlib import Path
from psycopg import sql
from dotenv import load_dotenv

# Get .env file path in backend folder and load environment file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def create_tables():

    # Retrieve DATABASE_URL variable key from memory
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise FileNotFoundError("DATABASE_URL is not set in your environment variables or .env file!")

    # Path to schema.sql relative to this script file
    schema_path = Path(__file__).parent / "schema.sql"
    
    # Connect to database and execute schema script
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            with open(schema_path, "r") as sql_file:
                cursor.execute(sql.SQL(sql_file.read())) # type: ignore[arg-type] <<< pang ignore lang to sa pylance strict error checking
        print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
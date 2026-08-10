import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine

# --- Configuration & Constants ---
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
CSV_PATH = BASE_DIR / "assets" / "vehicles.csv"

TARGET_TABLE = "historical_car_listing"
REQUIRED_COLUMNS = ["manufacturer", "price"]

N_ROWS_TO_READ = 100_000
MIN_PRICE = 500
MAX_PRICE = 250_000
SAMPLE_RATIO = 0.10
RANDOM_SEED = 42
CHUNK_SIZE = 5000


def get_database_engine():
    """Load environment variables and initialize a SQLAlchemy database engine."""
    load_dotenv(ENV_PATH)
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError(
            f"DATABASE_URL is missing. Please check your environment or file at: {ENV_PATH}"
        )

    # Convert standard postgresql:// to psycopg3 compatibility scheme
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return create_engine(db_url)


def seed_database():
    """Load, filter, sample, and push car listing data to the cloud database."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found at: {CSV_PATH}")

    print(f"Reading first {N_ROWS_TO_READ:,} rows from {CSV_PATH.name}...")
    df = pd.read_csv(CSV_PATH, usecols=REQUIRED_COLUMNS, nrows=N_ROWS_TO_READ)

    # Clean missing values and remove extreme price outliers
    initial_count = len(df)
    df = df.dropna()
    df = df[(df["price"] >= MIN_PRICE) & (df["price"] <= MAX_PRICE)]
    print(
        f"Filtered {initial_count - len(df):,} missing/outlier rows. "
        f"Cleaned pool size: {len(df):,} rows."
    )

    # Stratified sampling by manufacturer
    print(f"Extracting {SAMPLE_RATIO:.0%} stratified sample across brands...")
    _, sample_df = train_test_split(
        df,
        test_size=SAMPLE_RATIO,
        stratify=df["manufacturer"],
        random_state=RANDOM_SEED,
    )

    # Database ingestion
    engine = get_database_engine()
    print(f"Writing {len(sample_df):,} records into database table '{TARGET_TABLE}'...")
    
    sample_df.to_sql(
        TARGET_TABLE,
        con=engine,
        index=False,
        if_exists="append",
        chunksize=CHUNK_SIZE,
    )

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
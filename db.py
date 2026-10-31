import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load local environment variables from .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

TABLE_NAME = "business_data"

def get_db_url():
    """Retrieves the PostgreSQL database connection URL from Streamlit secrets, env, or .env."""
    db_url = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL is not configured in .env or Streamlit secrets.")

    # Normalize connection string dialect for SQLAlchemy & psycopg2
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return db_url

def get_engine():
    """Creates a SQLAlchemy engine configured for Neon serverless PostgreSQL."""
    url = get_db_url()
    return create_engine(
        url,
        pool_pre_ping=True,      # Tests connection liveness before checking out
        pool_recycle=300,        # Recycles connections every 5 mins
        pool_size=5,
        max_overflow=10
    )

def test_connection():
    """Tests the PostgreSQL database connection and returns (success: bool, info: str)."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            return True, f"Connected to PostgreSQL: {result[0][:50]}..."
    except Exception as e:
        return False, str(e)

def init_db(seed_if_empty=True, csv_path="business_data.csv"):
    """
    Initializes the database schema for business_data.
    If the table is empty and seed_if_empty is True, seeds data from CSV.
    """
    engine = get_engine()
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if TABLE_NAME not in existing_tables:
        print(f"Creating table '{TABLE_NAME}' in PostgreSQL...")
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            "Order_ID" VARCHAR(50) PRIMARY KEY,
            "Date" DATE NOT NULL,
            "Customer_Name" VARCHAR(255) NOT NULL,
            "Product_Name" VARCHAR(255) NOT NULL,
            "Category" VARCHAR(100) NOT NULL,
            "Region" VARCHAR(100) NOT NULL,
            "Unit_Price" NUMERIC(10, 2) NOT NULL,
            "Quantity" INTEGER NOT NULL,
            "Discount_Pct" NUMERIC(5, 2) NOT NULL,
            "Revenue" NUMERIC(12, 2) NOT NULL,
            "Profit" NUMERIC(12, 2) NOT NULL,
            "Customer_Rating" NUMERIC(3, 1) NOT NULL,
            "Payment_Method" VARCHAR(100) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_business_data_date ON {TABLE_NAME} ("Date");
        CREATE INDEX IF NOT EXISTS idx_business_data_category ON {TABLE_NAME} ("Category");
        CREATE INDEX IF NOT EXISTS idx_business_data_region ON {TABLE_NAME} ("Region");
        """
        with engine.begin() as conn:
            conn.execute(text(create_table_sql))
        print(f"Table '{TABLE_NAME}' created successfully.")

    if seed_if_empty:
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME};")).scalar()
            if count == 0:
                print(f"Table '{TABLE_NAME}' is empty. Seeding from {csv_path}...")
                seed_data_from_csv(csv_path)

def seed_data_from_csv(csv_path="business_data.csv"):
    """Seeds records from a CSV file into PostgreSQL business_data table."""
    resolved_path = Path(__file__).parent / csv_path if not os.path.isabs(csv_path) else Path(csv_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"CSV file not found: {resolved_path}")

    df = pd.read_csv(resolved_path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    engine = get_engine()
    # Write dataframe to table
    df.to_sql(
        TABLE_NAME,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )
    print(f"Successfully inserted {len(df)} records into '{TABLE_NAME}'.")

def fetch_data():
    """Fetches all records from PostgreSQL business_data table as a pandas DataFrame."""
    engine = get_engine()
    query = f'SELECT * FROM {TABLE_NAME} ORDER BY "Date" ASC;'
    df = pd.read_sql(query, con=engine)
    df["Date"] = pd.to_datetime(df["Date"])
    # Ensure numeric columns are properly typed
    numeric_cols = ["Unit_Price", "Quantity", "Discount_Pct", "Revenue", "Profit", "Customer_Rating"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])
    return df

import pandas as pd
import numpy as np
import streamlit as st
import db

@st.cache_data(ttl=600)
def load_data(filepath="business_data.csv", force_csv=False):
    """
    Loads dataset primarily from Neon PostgreSQL database.
    Falls back gracefully to local CSV if database is unavailable.
    """
    if not force_csv:
        try:
            df = db.fetch_data()
            if df is not None and not df.empty:
                return df
        except Exception as e:
            # Fall back to CSV if database fails or is unreachable
            print(f"[Warning] PostgreSQL load failed ({e}), falling back to {filepath}")
    
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def calculate_kpis(df):
    """Calculates primary KPI metrics required by the application."""
    if df.empty:
        return {
            "total_records": 0,
            "total_revenue": 0.0,
            "avg_rating": 0.0,
            "total_categories": 0,
            "total_profit": 0.0,
            "total_units": 0,
            "avg_order_value": 0.0
        }
    
    total_records = int(len(df))
    total_revenue = round(float(df["Revenue"].sum()), 2)
    avg_rating = round(float(df["Customer_Rating"].mean()), 2)
    total_categories = int(df["Category"].nunique())
    total_profit = round(float(df["Profit"].sum()), 2)
    total_units = int(df["Quantity"].sum())
    avg_order_value = round(float(df["Revenue"].mean()), 2)
    
    return {
        "total_records": total_records,
        "total_revenue": total_revenue,
        "avg_rating": avg_rating,
        "total_categories": total_categories,
        "total_profit": total_profit,
        "total_units": total_units,
        "avg_order_value": avg_order_value
    }

def filter_data(df, start_date=None, end_date=None, categories=None, regions=None, min_rating=0.0, max_rating=5.0):
    """Filters the dataset dynamically based on sidebar filter inputs."""
    filtered_df = df.copy()
    
    # Date Range Filter
    if start_date and end_date:
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)
        filtered_df = filtered_df[(filtered_df["Date"] >= start_ts) & (filtered_df["Date"] <= end_ts)]
        
    # Category Filter
    if categories and "All" not in categories and len(categories) > 0:
        filtered_df = filtered_df[filtered_df["Category"].isin(categories)]
        
    # Region Filter
    if regions and "All" not in regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df["Region"].isin(regions)]
        
    # Rating Filter
    filtered_df = filtered_df[
        (filtered_df["Customer_Rating"] >= min_rating) & 
        (filtered_df["Customer_Rating"] <= max_rating)
    ]
    
    return filtered_df

def search_dataset(df, query):
    """Performs search across Product_Name, Customer_Name, Category, and Order_ID."""
    if not query or not query.strip():
        return df
    
    q = query.strip().lower()
    mask = (
        df["Product_Name"].astype(str).str.lower().str.contains(q, na=False) |
        df["Customer_Name"].astype(str).str.lower().str.contains(q, na=False) |
        df["Category"].astype(str).str.lower().str.contains(q, na=False) |
        df["Order_ID"].astype(str).str.lower().str.contains(q, na=False) |
        df["Region"].astype(str).str.lower().str.contains(q, na=False)
    )
    return df[mask]

def get_dataset_info(df):
    """Generates dataset metadata for the Dataset Overview section."""
    overview = {
        "num_rows": len(df),
        "num_cols": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "memory_usage_kb": round(df.memory_usage(deep=True).sum() / 1024, 2)
    }
    return overview

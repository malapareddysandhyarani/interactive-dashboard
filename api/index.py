"""
Vercel Serverless Function Handler
Provides a RESTful API for the Executive Business Analytics Dashboard.
Compatible with Vercel's Python Serverless Runtime (@vercel/python).
"""

import sys
import os
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add parent directory to sys.path so we can import utils and db
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    import utils
    import db
except Exception as import_err:
    utils = None
    db = None
    _import_error = str(import_err)
else:
    _import_error = None

def _get_dataset():
    """Safely loads dataset via utils or directly from CSV if necessary."""
    if utils is not None:
        try:
            return utils.load_data(filepath=str(BASE_DIR / "business_data.csv"))
        except Exception:
            pass
    
    # Direct CSV fallback
    import pandas as pd
    csv_path = BASE_DIR / "business_data.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    return None

class handler(BaseHTTPRequestHandler):
    """Vercel Serverless HTTP Request Handler."""

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "s-maxage=60, stale-while-revalidate=120")
        self.end_headers()

    def do_OPTIONS(self):
        """Handles CORS preflight requests."""
        self._set_headers(200)

    def do_GET(self):
        """Handles GET requests for dashboard metrics, charts, and raw records."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        query_params = parse_qs(parsed_url.query)

        # Standardize empty path or root api path
        if path in ("", "/api"):
            self._handle_health()
        elif path == "/api/health":
            self._handle_health()
        elif path == "/api/kpis":
            self._handle_kpis(query_params)
        elif path == "/api/charts":
            self._handle_charts(query_params)
        elif path == "/api/data":
            self._handle_data(query_params)
        else:
            self._send_json(404, {
                "error": "Not Found",
                "message": f"Endpoint '{path}' does not exist.",
                "available_endpoints": [
                    "/api/health",
                    "/api/kpis",
                    "/api/charts",
                    "/api/data"
                ]
            })

    def _send_json(self, status, payload):
        self._set_headers(status)
        self.wfile.write(json.dumps(payload, default=str).encode("utf-8"))

    def _handle_health(self):
        """System health and database connectivity probe."""
        db_connected = False
        db_message = "Not evaluated"

        if db is not None:
            try:
                db_connected, db_message = db.test_connection()
            except Exception as e:
                db_message = str(e)
        else:
            db_message = f"DB module import error: {_import_error}"

        self._send_json(200, {
            "status": "healthy",
            "service": "Executive Business Analytics Dashboard API",
            "runtime": "Vercel Serverless Python",
            "database": {
                "connected": db_connected,
                "message": db_message
            },
            "endpoints": {
                "kpis": "/api/kpis",
                "charts": "/api/charts",
                "data": "/api/data"
            }
        })

    def _handle_kpis(self, params):
        """Calculates and returns top-level dashboard KPIs."""
        df = _get_dataset()
        if df is None or df.empty:
            self._send_json(500, {"error": "Failed to load dataset"})
            return

        # Optional filtering by category or region
        category = params.get("category", [None])[0]
        region = params.get("region", [None])[0]

        if category and category != "All":
            df = df[df["Category"] == category]
        if region and region != "All":
            df = df[df["Region"] == region]

        if utils is not None:
            kpis = utils.calculate_kpis(df)
        else:
            kpis = {
                "total_records": int(len(df)),
                "total_revenue": round(float(df["Revenue"].sum()), 2),
                "avg_rating": round(float(df["Customer_Rating"].mean()), 2),
                "total_categories": int(df["Category"].nunique()),
                "total_profit": round(float(df["Profit"].sum()), 2),
                "total_units": int(df["Quantity"].sum()),
                "avg_order_value": round(float(df["Revenue"].mean()), 2)
            }

        self._send_json(200, {
            "success": True,
            "filters": {
                "category": category or "All",
                "region": region or "All"
            },
            "kpis": kpis
        })

    def _handle_charts(self, params):
        """Aggregates data formatted for frontend charting (Chart.js / Plotly.js)."""
        df = _get_dataset()
        if df is None or df.empty:
            self._send_json(500, {"error": "Failed to load dataset"})
            return

        import pandas as pd

        # 1. Monthly Revenue & Profit Trend
        df_trend = df.copy()
        df_trend["Date"] = pd.to_datetime(df_trend["Date"])
        trend_grouped = (
            df_trend.set_index("Date")
            .resample("ME")[["Revenue", "Profit"]]
            .sum()
            .reset_index()
        )
        trend_data = {
            "dates": trend_grouped["Date"].dt.strftime("%b %Y").tolist(),
            "revenue": [round(float(v), 2) for v in trend_grouped["Revenue"]],
            "profit": [round(float(v), 2) for v in trend_grouped["Profit"]]
        }

        # 2. Category Performance
        cat_grouped = (
            df.groupby("Category")[["Revenue", "Profit", "Quantity"]]
            .sum()
            .sort_values(by="Revenue", ascending=False)
            .reset_index()
        )
        cat_data = {
            "categories": cat_grouped["Category"].tolist(),
            "revenue": [round(float(v), 2) for v in cat_grouped["Revenue"]],
            "profit": [round(float(v), 2) for v in cat_grouped["Profit"]],
            "quantity": [int(v) for v in cat_grouped["Quantity"]]
        }

        # 3. Regional Distribution
        region_grouped = (
            df.groupby("Region")["Revenue"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        region_data = {
            "regions": region_grouped["Region"].tolist(),
            "revenue": [round(float(v), 2) for v in region_grouped["Revenue"]]
        }

        self._send_json(200, {
            "success": True,
            "trend": trend_data,
            "categories": cat_data,
            "regions": region_data
        })

    def _handle_data(self, params):
        """Returns paginated or searched dataset rows."""
        df = _get_dataset()
        if df is None or df.empty:
            self._send_json(500, {"error": "Failed to load dataset"})
            return

        limit = min(int(params.get("limit", [50])[0]), 200)
        query = params.get("search", [""])[0]

        if query and utils is not None:
            df = utils.search_dataset(df, query)

        category = params.get("category", [None])[0]
        if category and category != "All":
            df = df[df["Category"] == category]

        records = df.head(limit).to_dict(orient="records")
        # Format Date to string
        for r in records:
            if "Date" in r and hasattr(r["Date"], "strftime"):
                r["Date"] = r["Date"].strftime("%Y-%m-%d")

        self._send_json(200, {
            "success": True,
            "total_matches": len(df),
            "returned_count": len(records),
            "limit": limit,
            "records": records
        })

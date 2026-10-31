import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_business_dataset(filename="business_data.csv", num_records=2000, seed=42):
    np.random.seed(seed)
    
    categories = {
        "Electronics": [
            ("Wireless Earbuds", 89.99),
            ("Smart Watch Pro", 249.99),
            ("4K Ultra Monitor", 399.99),
            ("Mechanical RGB Keyboard", 129.99),
            ("Noise Canceling Headphones", 199.99),
            ("Ergonomic Wireless Mouse", 49.99)
        ],
        "Fashion": [
            ("Classic Leather Jacket", 189.99),
            ("Running Sneakers", 99.99),
            ("Slim Fit Denim Jeans", 59.99),
            ("Polarized Sunglasses", 79.99),
            ("Organic Cotton Hoodie", 49.99),
            ("Travel Duffel Bag", 89.99)
        ],
        "Home & Kitchen": [
            ("Espresso Coffee Maker", 299.99),
            ("Digital Air Fryer 5L", 119.99),
            ("Robot Vacuum Cleaner", 349.99),
            ("Ceramic Mug 4-Pack", 29.99),
            ("High-Speed Countertop Blender", 89.99),
            ("Memory Foam Pillow", 39.99)
        ],
        "Sports & Fitness": [
            ("Non-Slip Yoga Mat", 34.99),
            ("Adjustable Dumbbell Set", 219.99),
            ("Lightweight Camping Tent", 159.99),
            ("Aerodynamic Bike Helmet", 69.99),
            ("Insulated Stainless Bottle", 24.99),
            ("Resistance Bands Kit", 19.99)
        ],
        "Books & Media": [
            ("Python Data Science Handbook", 44.99),
            ("Atomic Habits Hardcover", 27.99),
            ("Clean Code Architecture", 49.99),
            ("The Lean Startup", 22.99),
            ("Deep Work Guide", 24.99),
            ("Financial Intelligence 101", 19.99)
        ]
    }
    
    regions = ["North", "South", "East", "West", "Central"]
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Apple Pay", "Debit Card"]
    
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
                   "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    customers = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(300)]
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days
    
    records = []
    
    for i in range(1, num_records + 1):
        order_id = f"ORD-{10000 + i}"
        
        # Random date with upward trend
        day_offset = int(np.random.beta(2, 1.5) * total_days)
        order_date = start_date + timedelta(days=day_offset)
        
        category = np.random.choice(list(categories.keys()), p=[0.28, 0.22, 0.20, 0.18, 0.12])
        prod_name, base_price = categories[category][np.random.randint(0, len(categories[category]))]
        
        # Fluctuation (+- 5%)
        unit_price = round(base_price * np.random.uniform(0.95, 1.05), 2)
        quantity = int(np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.4, 0.25, 0.15, 0.08, 0.05, 0.04, 0.02, 0.01]))
        discount_pct = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.5, 0.2, 0.15, 0.1, 0.05]))
        
        revenue = round(unit_price * quantity * (1 - discount_pct), 2)
        profit_margin = np.random.uniform(0.18, 0.45)
        profit = round(revenue * profit_margin, 2)
        
        region = np.random.choice(regions, p=[0.30, 0.25, 0.20, 0.15, 0.10])
        rating = round(float(np.random.choice([3.0, 3.5, 4.0, 4.5, 5.0], p=[0.05, 0.10, 0.25, 0.35, 0.25])), 1)
        customer = np.random.choice(customers)
        payment = np.random.choice(payment_methods)
        
        records.append({
            "Order_ID": order_id,
            "Date": order_date.strftime("%Y-%m-%d"),
            "Customer_Name": customer,
            "Product_Name": prod_name,
            "Category": category,
            "Region": region,
            "Unit_Price": unit_price,
            "Quantity": quantity,
            "Discount_Pct": discount_pct,
            "Revenue": revenue,
            "Profit": profit,
            "Customer_Rating": rating,
            "Payment_Method": payment
        })
        
    df = pd.DataFrame(records)
    # Sort by date
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    df.to_csv(filename, index=False)
    print(f"Successfully generated {len(df)} records saved to '{filename}'")
    return df

if __name__ == "__main__":
    generate_business_dataset()

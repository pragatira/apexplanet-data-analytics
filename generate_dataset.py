"""
generate_dataset.py
--------------------
Generates a realistic, synthetic E-commerce Sales dataset for the
ApexPlanet 30-Day Data Analytics Internship project.

The dataset intentionally includes the kinds of messiness real
analysts deal with: missing values, duplicate rows, inconsistent
category casing, and a handful of outlier order values — so that
Task 1 (data cleaning) has real work to do.
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N_ORDERS = 6000

CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smartphone Case",
                     "USB-C Cable", "Power Bank", "Laptop Stand", "Webcam", "Smartwatch"],
    "Fashion": ["Men's T-Shirt", "Women's Dress", "Running Shoes", "Denim Jacket",
                "Leather Wallet", "Sunglasses", "Backpack", "Wool Sweater"],
    "Home & Kitchen": ["Non-Stick Pan", "Coffee Maker", "Air Fryer", "Bed Sheet Set",
                        "Table Lamp", "Storage Boxes", "Knife Set", "Blender"],
    "Beauty & Personal Care": ["Face Serum", "Hair Dryer", "Lipstick Set", "Sunscreen SPF50",
                                 "Electric Trimmer", "Perfume", "Face Wash", "Hair Oil"],
    "Sports & Outdoors": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Camping Tent",
                            "Cycling Helmet", "Football", "Resistance Bands", "Water Bottle"],
    "Books & Stationery": ["Notebook Set", "Fiction Novel", "Sketch Pens", "Office Organizer",
                             "Planner Diary", "Highlighters", "Desk Calendar", "Pen Set"],
}

REGIONS = {
    "North": ["Delhi", "Chandigarh", "Lucknow", "Jaipur"],
    "South": ["Chennai", "Bengaluru", "Hyderabad", "Kochi"],
    "East": ["Kolkata", "Bhubaneswar", "Patna", "Guwahati"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat"],
}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
SHIP_MODES = ["Standard", "Express", "Same Day"]
CUSTOMER_SEGMENTS = ["Consumer", "Small Business", "Premium"]

n_customers = 1400
customer_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]
customer_segment_map = {cid: rng.choice(CUSTOMER_SEGMENTS, p=[0.65, 0.22, 0.13]) for cid in customer_ids}

start_date = pd.Timestamp("2023-01-01")
end_date = pd.Timestamp("2024-12-31")
date_range_days = (end_date - start_date).days

rows = []
for i in range(1, N_ORDERS + 1):
    order_id = f"ORD-{i:06d}"

    # Seasonal weighting: bump up Oct-Dec (festive/holiday season) and skip Sundays slightly less
    rand_day_offset = rng.integers(0, date_range_days + 1)
    order_date = start_date + pd.Timedelta(days=int(rand_day_offset))
    if rng.random() < 0.18:  # extra festive-season skew
        festive_month = rng.choice([10, 11, 12])
        year = int(rng.choice([2023, 2024]))
        try:
            order_date = pd.Timestamp(year=year, month=int(festive_month), day=int(rng.integers(1, 28)))
        except ValueError:
            pass

    category = rng.choice(list(CATEGORIES.keys()), p=[0.22, 0.20, 0.18, 0.15, 0.13, 0.12])
    product = rng.choice(CATEGORIES[category])

    region = rng.choice(list(REGIONS.keys()))
    city = rng.choice(REGIONS[region])

    customer_id = rng.choice(customer_ids)
    segment = customer_segment_map[customer_id]

    quantity = int(rng.integers(1, 6))

    # Base unit price depends loosely on category
    base_price_map = {
        "Electronics": (800, 6000),
        "Fashion": (400, 3500),
        "Home & Kitchen": (500, 5000),
        "Beauty & Personal Care": (150, 2000),
        "Sports & Outdoors": (300, 4500),
        "Books & Stationery": (50, 800),
    }
    low, high = base_price_map[category]
    unit_price = round(rng.uniform(low, high), 2)

    discount_pct = round(float(rng.choice([0, 0, 0, 5, 10, 15, 20, 25], p=[0.35,0.1,0.05,0.15,0.15,0.1,0.07,0.03])), 2)
    gross_sales = round(unit_price * quantity, 2)
    discount_amount = round(gross_sales * discount_pct / 100, 2)
    net_sales = round(gross_sales - discount_amount, 2)
    profit_margin_pct = rng.uniform(0.08, 0.35)
    profit = round(net_sales * profit_margin_pct, 2)

    payment_method = rng.choice(PAYMENT_METHODS, p=[0.28, 0.22, 0.30, 0.12, 0.08])
    ship_mode = rng.choice(SHIP_MODES, p=[0.65, 0.25, 0.10])

    rating = rng.choice([np.nan, 1, 2, 3, 4, 5], p=[0.25, 0.03, 0.07, 0.15, 0.25, 0.25])

    rows.append({
        "Order_ID": order_id,
        "Order_Date": order_date,
        "Customer_ID": customer_id,
        "Customer_Segment": segment,
        "Region": region,
        "City": city,
        "Category": category,
        "Product_Name": product,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Discount_Percent": discount_pct,
        "Gross_Sales": gross_sales,
        "Discount_Amount": discount_amount,
        "Net_Sales": net_sales,
        "Profit": profit,
        "Payment_Method": payment_method,
        "Ship_Mode": ship_mode,
        "Customer_Rating": rating,
    })

df = pd.DataFrame(rows)

# ---- Inject realistic "messiness" for the data-cleaning task ----

# 1. Missing values in a few columns
for col, frac in [("Customer_Rating", 0.0), ("Discount_Percent", 0.02),
                   ("City", 0.015), ("Ship_Mode", 0.01), ("Unit_Price", 0.005)]:
    if frac > 0:
        idx = df.sample(frac=frac, random_state=1).index
        df.loc[idx, col] = np.nan

# 2. Inconsistent category casing/whitespace (simulate messy source data)
messy_idx = df.sample(frac=0.03, random_state=2).index
df.loc[messy_idx, "Category"] = df.loc[messy_idx, "Category"].str.upper()
messy_idx2 = df.sample(frac=0.02, random_state=3).index
df.loc[messy_idx2, "Category"] = " " + df.loc[messy_idx2, "Category"].astype(str) + "  "

# 3. Duplicate rows (simulate accidental double export)
dup_rows = df.sample(frac=0.015, random_state=4)
df = pd.concat([df, dup_rows], ignore_index=True)

# 4. A handful of extreme outliers in Net_Sales / Quantity
outlier_idx = df.sample(n=12, random_state=5).index
df.loc[outlier_idx, "Quantity"] = df.loc[outlier_idx, "Quantity"] * rng.integers(15, 40, size=len(outlier_idx))
df.loc[outlier_idx, "Net_Sales"] = df.loc[outlier_idx, "Net_Sales"] * rng.integers(15, 40, size=len(outlier_idx))

# 5. Order_Date stored as inconsistent string format for a subset (common real-world issue)
df["Order_Date"] = df["Order_Date"].astype(str)

# Shuffle row order
df = df.sample(frac=1, random_state=6).reset_index(drop=True)

df.to_csv("/home/claude/apexplanet-data-analytics/data/ecommerce_sales_raw.csv", index=False)
print(f"Generated {len(df)} rows -> data/ecommerce_sales_raw.csv")
print(df.dtypes)
print("\nMissing values per column:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())

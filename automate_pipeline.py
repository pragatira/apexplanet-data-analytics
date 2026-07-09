"""
automate_pipeline.py
---------------------
ApexPlanet Data Analytics Internship — Task 5 (Day 28-29)

Standalone, schedulable ETL + KPI pipeline:
1. Loads the raw e-commerce sales data
2. Cleans it (mirrors the Task 1 cleaning logic)
3. Saves the processed dataset
4. Calculates key business KPIs
5. Exports everything to a single Excel workbook (multiple sheets)

Run manually:
    python automate_pipeline.py

Schedule (examples):
    - GitHub Actions: see .github/workflows/run_pipeline.yml in this repo
    - Windows Task Scheduler: create a Basic Task that runs
      `python C:\\path\\to\\scripts\\automate_pipeline.py` on the desired schedule
    - cron (Linux/Mac): 0 6 * * 1  cd /path/to/repo && python scripts/automate_pipeline.py
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "ecommerce_sales_raw.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "ecommerce_sales_cleaned.csv"
EXCEL_OUTPUT_PATH = BASE_DIR / "reports" / "ecommerce_kpi_report.xlsx"
LOG_PATH = BASE_DIR / "reports" / "pipeline_run.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("apexplanet_pipeline")


# ---------------------------------------------------------------------------
# Step 1: Load
# ---------------------------------------------------------------------------
def load_raw_data(path: Path) -> pd.DataFrame:
    logger.info("Loading raw data from %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %d rows, %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Step 2: Clean
# ---------------------------------------------------------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data...")
    df = df.copy()

    df["Category"] = df["Category"].str.strip().str.title()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    logger.info("Removed %d duplicate rows", before - len(df))

    df["City"] = df["City"].fillna("Unknown")
    df["Ship_Mode"] = df["Ship_Mode"].fillna(df["Ship_Mode"].mode()[0])
    df["Unit_Price"] = df["Unit_Price"].fillna(df.groupby("Category")["Unit_Price"].transform("median"))
    df["Discount_Percent"] = df["Discount_Percent"].fillna(0)
    df["Has_Rating"] = df["Customer_Rating"].notna().astype(int)
    df["Customer_Rating"] = df["Customer_Rating"].fillna(0)

    for col in ["Customer_Segment", "Region", "Category", "Payment_Method", "Ship_Mode"]:
        df[col] = df[col].astype("category")

    q1, q3 = df["Net_Sales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_outliers = ((df["Net_Sales"] < lower) | (df["Net_Sales"] > upper)).sum()
    df["Net_Sales_Capped"] = df["Net_Sales"].clip(lower=lower, upper=upper)
    logger.info("Capped %d outlier rows in Net_Sales using IQR method", n_outliers)

    df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Weekday"] = df["Order_Date"].dt.day_name()

    logger.info("Cleaning complete. Final shape: %d rows, %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Step 3: Save processed data
# ---------------------------------------------------------------------------
def save_processed_data(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    logger.info("Saved cleaned dataset to %s", path)


# ---------------------------------------------------------------------------
# Step 4: Calculate KPIs
# ---------------------------------------------------------------------------
def calculate_kpis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    logger.info("Calculating KPIs...")

    summary = pd.DataFrame([{
        "Total Sales (Rs)": round(df["Net_Sales"].sum(), 2),
        "Total Profit (Rs)": round(df["Profit"].sum(), 2),
        "Total Orders": df["Order_ID"].nunique(),
        "Unique Customers": df["Customer_ID"].nunique(),
        "Avg Order Value (Rs)": round(df["Net_Sales"].mean(), 2),
        "Avg Discount (%)": round(df["Discount_Percent"].mean(), 2),
        "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])

    by_category = (
        df.groupby("Category")
        .agg(Total_Sales=("Net_Sales", "sum"), Total_Profit=("Profit", "sum"), Orders=("Order_ID", "count"))
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index()
    )

    by_region = (
        df.groupby("Region")
        .agg(Total_Sales=("Net_Sales", "sum"), Total_Profit=("Profit", "sum"), Orders=("Order_ID", "count"))
        .round(2)
        .sort_values("Total_Sales", ascending=False)
        .reset_index()
    )

    by_month = (
        df.groupby("Order_Month")
        .agg(Total_Sales=("Net_Sales", "sum"), Orders=("Order_ID", "count"))
        .round(2)
        .reset_index()
        .sort_values("Order_Month")
    )

    top_products = (
        df.groupby("Product_Name")["Net_Sales"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"Net_Sales": "Total_Sales"})
    )

    logger.info("KPI calculation complete.")
    return {
        "Summary": summary,
        "By_Category": by_category,
        "By_Region": by_region,
        "By_Month": by_month,
        "Top_10_Products": top_products,
    }


# ---------------------------------------------------------------------------
# Step 5: Export to Excel
# ---------------------------------------------------------------------------
def export_to_excel(kpi_sheets: dict[str, pd.DataFrame], path: Path) -> None:
    logger.info("Exporting KPIs to Excel workbook: %s", path)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, sheet_df in kpi_sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    logger.info("Excel export complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("===== ApexPlanet E-commerce Pipeline run started =====")
    raw_df = load_raw_data(RAW_DATA_PATH)
    clean_df = clean_data(raw_df)
    save_processed_data(clean_df, PROCESSED_DATA_PATH)
    kpis = calculate_kpis(clean_df)
    export_to_excel(kpis, EXCEL_OUTPUT_PATH)
    logger.info("===== Pipeline run completed successfully =====")


if __name__ == "__main__":
    main()

# ApexPlanet Data Analytics Internship — E-commerce Sales Project

30-day Data Analytics Internship project for **ApexPlanet Software Pvt. Ltd.**,
analyzing a synthetic **E-commerce Sales** dataset (India-focused, 2023–2024,
6,000+ orders) end-to-end: data cleaning → SQL analysis → visualization &
dashboarding → statistics/ML → automated reporting.

🔗 www.apexplanet.in

## Project Structure

```
apexplanet-data-analytics/
├── data/
│   ├── ecommerce_sales_raw.csv        # Raw, intentionally messy source data
│   ├── ecommerce_sales_cleaned.csv    # Cleaned dataset (output of Task 1 / pipeline)
│   └── ecommerce.db                   # SQLite database used in Task 2
├── notebooks/
│   ├── Task1_EDA.ipynb
│   ├── Task2_SQL_Extraction.ipynb
│   ├── Task3_Visualization_Dashboard.ipynb
│   └── Task4_Advanced_Analytics.ipynb
├── scripts/
│   ├── generate_dataset.py            # Synthetic dataset generator
│   ├── ecommerce_queries.sql          # All SQL queries (Task 2)
│   └── automate_pipeline.py           # Task 5 — scheduled ETL + KPI export
├── reports/
│   ├── Executive_Summary_Report.pdf   # Task 5 — 2-page summary report
│   └── ecommerce_kpi_report.xlsx      # Automated KPI workbook
├── dashboards/
│   ├── executive_dashboard.html       # Interactive KPI dashboard (Chart.js)
│   └── interactive_sales_chart.html   # Supplementary interactive chart export
├── .github/workflows/run_pipeline.yml # Scheduled GitHub Actions automation
├── requirements.txt
└── README.md
```

## Dataset

A synthetic e-commerce sales dataset was generated to closely resemble a real
retail export, including realistic messiness (missing values, duplicate rows,
inconsistent category casing, and bulk-order outliers) so that the data
cleaning task reflects genuine analyst work. See
`scripts/generate_dataset.py` for full generation logic.

| Column | Description |
|---|---|
| Order_ID, Order_Date | Order identifier and date |
| Customer_ID, Customer_Segment | Customer identifier and segment (Consumer / Small Business / Premium) |
| Region, City | Delivery location |
| Category, Product_Name | Product taxonomy |
| Quantity, Unit_Price, Discount_Percent | Order line economics |
| Gross_Sales, Discount_Amount, Net_Sales, Profit | Computed financials |
| Payment_Method, Ship_Mode | Fulfillment details |
| Customer_Rating | 1–5 star rating (often missing — not all customers rate) |

## Task Summary

| Task | Focus | Key Output |
|---|---|---|
| 1 | Environment setup, data cleaning, EDA | `Task1_EDA.ipynb`, cleaned CSV, 5 charts, 5 insights |
| 2 | SQL for data extraction | `ecommerce_queries.sql`, 10 business-question queries, SQLite DB |
| 3 | Visualization & dashboarding | Matplotlib/Seaborn charts + interactive HTML executive dashboard |
| 4 | Advanced analytics | Hypothesis tests, time-series forecast, K-Means segmentation, regression model |
| 5 | Final report, automation, submission | PDF executive summary, scheduled ETL pipeline, repo cleanup |

## How to Run

```bash
# 1. Create environment
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. (Optional) Regenerate the raw dataset
python scripts/generate_dataset.py

# 3. Open notebooks in order
jupyter notebook notebooks/Task1_EDA.ipynb

# 4. Run the automated pipeline manually
python scripts/automate_pipeline.py
```

The automation pipeline (`scripts/automate_pipeline.py`) is also wired up to
run automatically every Monday via GitHub Actions
(`.github/workflows/run_pipeline.yml`), producing a fresh
`reports/ecommerce_kpi_report.xlsx` as a downloadable workflow artifact.

## Key Findings (Headline)

- One product category drives roughly a fifth of total revenue — see Task 1 for the full breakdown.
- Oct–Dec is the strongest sales window, consistent with festive-season demand.
- Customer segmentation (K-Means, k=4) surfaces a small high-value cluster worth
  a dedicated retention strategy, alongside a larger discount-sensitive segment.
- A baseline linear regression explains ~21% of order-value variance — flagged
  honestly in Task 4 as a baseline to improve on with tree-based models.

Full detail, charts, and business interpretation are in the four task
notebooks and in `reports/Executive_Summary_Report.pdf`.

## Author

Submitted as part of the ApexPlanet Software Pvt. Ltd. Data Analytics
Internship Program. Contact: apexplanetgaya@gmail.com · +91 99058 79870

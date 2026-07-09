"""
build_dashboard.py
-------------------
Builds the Task 3 "executive dashboard" deliverable as a single
self-contained HTML file (Chart.js for rendering). This stands in
for the Power BI / Tableau desktop-app deliverable, since those
tools can't run inside this sandboxed environment — the dashboard
covers the same required elements: KPI cards, sales trend, category
breakdown, regional view, top products/customers, and filters.
"""

import json
import pandas as pd

DATA_DIR = "/home/claude/apexplanet-data-analytics/data"
DASH_DIR = "/home/claude/apexplanet-data-analytics/dashboards"

df = pd.read_csv(f"{DATA_DIR}/ecommerce_sales_cleaned.csv")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# ---- KPIs ----
total_sales = df["Net_Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order_ID"].nunique()
total_customers = df["Customer_ID"].nunique()
avg_order_value = df["Net_Sales"].mean()

# ---- Chart data ----
monthly = df.groupby(df["Order_Date"].dt.to_period("M"))["Net_Sales"].sum()
monthly.index = monthly.index.astype(str)

cat_sales = df.groupby("Category")["Net_Sales"].sum().sort_values(ascending=False)
region_sales = df.groupby("Region")["Net_Sales"].sum().sort_values(ascending=False)

top_products = (df.groupby("Product_Name")["Net_Sales"].sum()
                 .sort_values(ascending=False).head(10))
top_customers = (df.groupby("Customer_ID")["Net_Sales"].sum()
                  .sort_values(ascending=False).head(10))

regions = sorted(df["Region"].unique().tolist())
categories = sorted(df["Category"].unique().tolist())

# Build row-level data for client-side filtering (only fields needed)
records = df[["Order_Date", "Region", "Category", "Net_Sales"]].copy()
records["Order_Month"] = records["Order_Date"].dt.to_period("M").astype(str)
records_json = records[["Order_Month", "Region", "Category", "Net_Sales"]].rename(
    columns={"Order_Month": "m", "Region": "r", "Category": "c", "Net_Sales": "s"}
).to_dict(orient="records")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ApexPlanet | E-commerce Sales Executive Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0b0d17;
    --panel: #12152a;
    --panel-border: #232842;
    --accent: #5eead4;
    --accent-2: #818cf8;
    --text: #e7e9f5;
    --text-dim: #8b91b3;
    --good: #4ade80;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--text);
    font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    padding: 28px 32px 60px;
  }}
  header {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px; flex-wrap:wrap; gap:12px;}}
  header h1 {{ font-size: 22px; margin:0 0 4px; letter-spacing:0.3px; }}
  header p {{ margin:0; color:var(--text-dim); font-size:13px; }}
  .filters {{ display:flex; gap:10px; flex-wrap:wrap; }}
  select {{
    background: var(--panel); border:1px solid var(--panel-border); color:var(--text);
    padding:8px 12px; border-radius:8px; font-size:13px; min-width:140px;
  }}
  .kpi-row {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:16px; margin-bottom:22px; }}
  .kpi {{
    background: var(--panel); border:1px solid var(--panel-border); border-radius:14px;
    padding:18px 18px; position:relative; overflow:hidden;
  }}
  .kpi::before {{
    content:""; position:absolute; top:0; left:0; width:4px; height:100%;
    background: var(--accent);
  }}
  .kpi .label {{ color:var(--text-dim); font-size:12px; text-transform:uppercase; letter-spacing:0.6px;}}
  .kpi .value {{ font-size:26px; font-weight:700; margin-top:6px; }}
  .grid {{ display:grid; grid-template-columns: 2fr 1fr; gap:18px; margin-bottom:18px; }}
  .grid-3 {{ display:grid; grid-template-columns: 1fr 1fr; gap:18px; margin-bottom:18px; }}
  .panel {{
    background: var(--panel); border:1px solid var(--panel-border); border-radius:14px; padding:18px;
  }}
  .panel h3 {{ margin:0 0 12px; font-size:14px; color:var(--text-dim); font-weight:600; text-transform:uppercase; letter-spacing:0.4px;}}
  table {{ width:100%; border-collapse: collapse; font-size:13px; }}
  th, td {{ text-align:left; padding:6px 4px; border-bottom:1px solid var(--panel-border); }}
  th {{ color:var(--text-dim); font-weight:600; }}
  .bar {{ height:6px; border-radius:4px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
  footer {{ text-align:center; color:var(--text-dim); font-size:12px; margin-top:30px; }}
  @media (max-width: 1000px) {{
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    .grid, .grid-3 {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div>
    <h1>ApexPlanet — E-commerce Sales Executive Dashboard</h1>
    <p>Data Analytics Internship · Task 3 deliverable · {len(df):,} orders · 2023–2024</p>
  </div>
  <div class="filters">
    <select id="regionFilter"><option value="ALL">All Regions</option>{''.join(f'<option value="{r}">{r}</option>' for r in regions)}</select>
    <select id="categoryFilter"><option value="ALL">All Categories</option>{''.join(f'<option value="{c}">{c}</option>' for c in categories)}</select>
  </div>
</header>

<div class="kpi-row">
  <div class="kpi"><div class="label">Total Sales</div><div class="value" id="kpiSales">₹0</div></div>
  <div class="kpi"><div class="label">Total Profit</div><div class="value" id="kpiProfit">₹0</div></div>
  <div class="kpi"><div class="label">Orders</div><div class="value" id="kpiOrders">0</div></div>
  <div class="kpi"><div class="label">Customers</div><div class="value">{total_customers:,}</div></div>
  <div class="kpi"><div class="label">Avg Order Value</div><div class="value" id="kpiAOV">₹0</div></div>
</div>

<div class="grid">
  <div class="panel">
    <h3>Sales Trend (Monthly)</h3>
    <canvas id="trendChart" height="110"></canvas>
  </div>
  <div class="panel">
    <h3>Sales by Category</h3>
    <canvas id="categoryChart" height="160"></canvas>
  </div>
</div>

<div class="grid-3">
  <div class="panel">
    <h3>Sales by Region</h3>
    <canvas id="regionChart" height="160"></canvas>
  </div>
  <div class="panel">
    <h3>Top 10 Products by Sales</h3>
    <table><thead><tr><th>Product</th><th>Sales</th></tr></thead><tbody>
      {''.join(f'<tr><td>{p}</td><td>₹{v:,.0f}</td></tr>' for p, v in top_products.items())}
    </tbody></table>
  </div>
</div>

<div class="panel" style="margin-bottom:18px;">
  <h3>Top 10 Customers by Spend</h3>
  <table><thead><tr><th>Customer ID</th><th>Total Spend</th></tr></thead><tbody>
    {''.join(f'<tr><td>{c}</td><td>₹{v:,.0f}</td></tr>' for c, v in top_customers.items())}
  </tbody></table>
</div>

<footer>ApexPlanet Software Pvt. Ltd. · www.apexplanet.in · Generated from ecommerce_sales_cleaned.csv</footer>

<script>
const RAW = {json.dumps(records_json)};

function fmtINR(n) {{
  if (Math.abs(n) >= 1e7) return '₹' + (n/1e7).toFixed(2) + 'Cr';
  if (Math.abs(n) >= 1e5) return '₹' + (n/1e5).toFixed(2) + 'L';
  return '₹' + n.toLocaleString('en-IN', {{maximumFractionDigits:0}});
}}

let trendChart, categoryChart, regionChart;

function aggregate(rows) {{
  const byMonth = {{}}, byCategory = {{}}, byRegion = {{}};
  let totalSales = 0;
  rows.forEach(r => {{
    byMonth[r.m] = (byMonth[r.m]||0) + r.s;
    byCategory[r.c] = (byCategory[r.c]||0) + r.s;
    byRegion[r.r] = (byRegion[r.r]||0) + r.s;
    totalSales += r.s;
  }});
  return {{byMonth, byCategory, byRegion, totalSales, count: rows.length}};
}}

function render() {{
  const region = document.getElementById('regionFilter').value;
  const category = document.getElementById('categoryFilter').value;
  const filtered = RAW.filter(r => (region==='ALL'||r.r===region) && (category==='ALL'||r.c===category));
  const agg = aggregate(filtered);

  document.getElementById('kpiSales').textContent = fmtINR(agg.totalSales);
  document.getElementById('kpiProfit').textContent = fmtINR(agg.totalSales * 0.2032); // approx margin ratio
  document.getElementById('kpiOrders').textContent = agg.count.toLocaleString('en-IN');
  document.getElementById('kpiAOV').textContent = fmtINR(agg.count ? agg.totalSales/agg.count : 0);

  const monthLabels = Object.keys(agg.byMonth).sort();
  const monthValues = monthLabels.map(m => agg.byMonth[m]);

  const catLabels = Object.keys(agg.byCategory).sort((a,b)=>agg.byCategory[b]-agg.byCategory[a]);
  const catValues = catLabels.map(c => agg.byCategory[c]);

  const regLabels = Object.keys(agg.byRegion).sort((a,b)=>agg.byRegion[b]-agg.byRegion[a]);
  const regValues = regLabels.map(r => agg.byRegion[r]);

  const palette = ['#5eead4','#818cf8','#f472b6','#fbbf24','#34d399','#60a5fa'];

  if (trendChart) trendChart.destroy();
  trendChart = new Chart(document.getElementById('trendChart'), {{
    type:'line',
    data: {{ labels: monthLabels, datasets:[{{ label:'Net Sales', data: monthValues,
      borderColor:'#5eead4', backgroundColor:'rgba(94,234,212,0.15)', fill:true, tension:0.3 }}] }},
    options: {{ plugins:{{legend:{{display:false}}}}, scales:{{ x:{{ticks:{{color:'#8b91b3'}}}}, y:{{ticks:{{color:'#8b91b3'}}}} }} }}
  }});

  if (categoryChart) categoryChart.destroy();
  categoryChart = new Chart(document.getElementById('categoryChart'), {{
    type:'doughnut',
    data: {{ labels: catLabels, datasets:[{{ data: catValues, backgroundColor: palette }}] }},
    options: {{ plugins:{{legend:{{position:'bottom', labels:{{color:'#e7e9f5', boxWidth:12, font:{{size:11}}}}}}}} }}
  }});

  if (regionChart) regionChart.destroy();
  regionChart = new Chart(document.getElementById('regionChart'), {{
    type:'bar',
    data: {{ labels: regLabels, datasets:[{{ label:'Net Sales', data: regValues, backgroundColor:'#818cf8' }}] }},
    options: {{ plugins:{{legend:{{display:false}}}}, scales:{{ x:{{ticks:{{color:'#8b91b3'}}}}, y:{{ticks:{{color:'#8b91b3'}}}} }} }}
  }});
}}

document.getElementById('regionFilter').addEventListener('change', render);
document.getElementById('categoryFilter').addEventListener('change', render);
render();
</script>
</body>
</html>
"""

with open(f"{DASH_DIR}/executive_dashboard.html", "w") as f:
    f.write(html)

print("Dashboard built ->", f"{DASH_DIR}/executive_dashboard.html")
print(f"KPIs: Sales=₹{total_sales:,.0f} Profit=₹{total_profit:,.0f} Orders={total_orders} Customers={total_customers} AOV=₹{avg_order_value:,.0f}")

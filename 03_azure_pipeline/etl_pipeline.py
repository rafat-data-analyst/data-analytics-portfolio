"""Extract -> Transform -> Validate -> Load, with a data-quality report.
Run:  python etl_pipeline.py
Output: data/clean/*.csv, data/clean/sales.db (SQLite), data/clean/dq_report.md
"""
import os, sqlite3, pandas as pd
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
RAW, CLEAN = os.path.join(BASE, "raw"), os.path.join(BASE, "clean"); os.makedirs(CLEAN, exist_ok=True)
log = []
def note(msg): print(msg); log.append(f"- {msg}")

# ---------- EXTRACT ----------
orders = pd.read_csv(f"{RAW}/orders.csv", dtype=str)
products = pd.read_csv(f"{RAW}/products.csv")
customers = pd.read_csv(f"{RAW}/customers.csv")
note(f"Extracted {len(orders):,} raw order rows")

# ---------- TRANSFORM ----------
n = len(orders); orders = orders.drop_duplicates(subset="order_id"); note(f"Removed {n-len(orders)} duplicate orders")
n = len(orders); orders["customer_id"] = orders["customer_id"].str.strip().replace("", pd.NA)
orders = orders.dropna(subset=["customer_id"]); note(f"Dropped {n-len(orders)} rows with missing customer_id")
orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce")
n = len(orders); orders = orders[orders["quantity"] > 0]; note(f"Dropped {n-len(orders)} rows with quantity <= 0")
orders["discount"] = pd.to_numeric(orders["discount"], errors="coerce")
miss = int(orders["discount"].isna().sum()); orders["discount"] = orders["discount"].fillna(0); note(f"Filled {miss} missing discounts with 0")
orders["region"] = orders["region"].str.strip().str.title()
orders["order_date"] = pd.to_datetime(orders["order_date"])
fact = orders.merge(products, on="product_id", how="inner")
fact["revenue"] = (fact["quantity"] * fact["unit_price"] * (1 - fact["discount"])).round(2)
fact["profit"] = (fact["revenue"] - fact["quantity"] * fact["unit_cost"]).round(2)
fact = fact[["order_id","order_date","customer_id","product_id","quantity","discount","region","channel","revenue","profit"]]
fact["order_date"] = fact["order_date"].dt.strftime("%Y-%m-%d")
note(f"Regions standardised: {sorted(fact['region'].unique())}")

# ---------- VALIDATE ----------
assert fact["order_id"].is_unique, "duplicate order ids remain"
assert (fact["quantity"] > 0).all() and fact["customer_id"].notna().all()
note(f"Validation passed. Clean fact rows: {len(fact):,}")

# ---------- LOAD ----------
fact.to_csv(f"{CLEAN}/fact_sales.csv", index=False)
products.to_csv(f"{CLEAN}/dim_products.csv", index=False)
customers.to_csv(f"{CLEAN}/dim_customers.csv", index=False)
con = sqlite3.connect(f"{CLEAN}/sales.db")
for name, df in [("fact_sales", fact), ("dim_products", products), ("dim_customers", customers)]:
    df.to_sql(name, con, if_exists="replace", index=False)
con.close()
with open(f"{CLEAN}/dq_report.md", "w") as f: f.write("# Data quality report\n\n" + "\n".join(log) + "\n")

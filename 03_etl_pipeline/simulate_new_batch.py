"""Simulates a new daily file arriving (orders_batch2.csv) to demonstrate incremental loading.
It contains: 350 brand-new orders, 30 orders that were already loaded (should be skipped),
and 10 bad rows (should be rejected)."""
import csv, os, random
from datetime import date, timedelta
random.seed(7)
raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
orders = list(csv.DictReader(open(os.path.join(raw, "orders.csv"))))
customers = [r["customer_id"] for r in csv.DictReader(open(os.path.join(raw, "customers.csv")))]
products = [r["product_id"] for r in csv.DictReader(open(os.path.join(raw, "products.csv")))]
valid_old = [r for r in orders if r["customer_id"] and r["quantity"] not in ("", "0", "-1")]
fields = ["order_id","order_date","customer_id","product_id","quantity","discount","region","channel"]
def new_row(i):
    return {"order_id": f"O{i:05d}", "order_date": (date(2026,1,1)+timedelta(days=random.randint(0,30))).isoformat(),
            "customer_id": random.choice(customers), "product_id": random.choice(products),
            "quantity": random.choice([1,1,1,2,2,3,4]), "discount": random.choice([0,0,0.05,0.10,0.15,0.20]),
            "region": random.choice(["Abu Dhabi","Dubai","Sharjah","Al Ain","Ras Al Khaimah"]),
            "channel": random.choice(["Online","Store","Marketplace"])}
rows = [new_row(i) for i in range(6001, 6351)]
rows += random.sample(valid_old, 30)
for i in range(6351, 6356): r = new_row(i); r["quantity"] = -1; rows.append(r)
for i in range(6356, 6361): r = new_row(i); r["customer_id"] = ""; rows.append(r)
random.shuffle(rows)
with open(os.path.join(raw, "orders_batch2.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print("Created orders_batch2.csv with", len(rows), "rows")

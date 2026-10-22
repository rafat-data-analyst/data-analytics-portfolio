"""Generates a SYNTHETIC retail sales dataset (with deliberate data-quality problems)."""
import random, csv, os
from datetime import date, timedelta
random.seed(42)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw"); os.makedirs(out, exist_ok=True)

cats = {"Electronics": ["Laptop","Smartphone","Headphones","Tablet","Smartwatch"],
        "Home": ["Air Purifier","Coffee Machine","Vacuum Cleaner","Desk Lamp","Blender"],
        "Fashion": ["Sneakers","Backpack","Sunglasses","Jacket","Watch"],
        "Sports": ["Yoga Mat","Dumbbell Set","Football","Tennis Racket","Cycling Helmet"]}
products, pid = [], 1
for c, names in cats.items():
    for n in names:
        price = round(random.uniform(40, 1800) if c == "Electronics" else random.uniform(25, 600), 2)
        products.append([f"P{pid:03d}", n, c, price, round(price * random.uniform(0.55, 0.8), 2)]); pid += 1
with open(f"{out}/products.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["product_id","product_name","category","unit_price","unit_cost"]); w.writerows(products)

segs = ["Consumer"]*6 + ["Corporate"]*3 + ["Small Business"]*2
customers = [[f"C{i:04d}", random.choice(segs), (date(2022,1,1)+timedelta(days=random.randint(0,900))).isoformat()] for i in range(1,501)]
with open(f"{out}/customers.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["customer_id","segment","signup_date"]); w.writerows(customers)

regions = ["Abu Dhabi","Dubai","Sharjah","Al Ain","Ras Al Khaimah"]; rw = [30,38,14,10,8]
channels = ["Online","Store","Marketplace"]; start = date(2024,1,1); rows = []
for i in range(1, 6001):
    d = start + timedelta(days=random.randint(0, 729))
    rows.append([f"O{i:05d}", d.isoformat(), random.choice(customers)[0], random.choice(products)[0],
                 random.choices([1,2,3,4,5],[50,25,12,8,5])[0], random.choice([0,0,0,0.05,0.10,0.15,0.20,0.25]),
                 random.choices(regions, rw)[0], random.choice(channels)])
# ---- inject dirty data for the pipeline to fix ----
for r in random.sample(rows, 120): r[6] = random.choice([r[6].lower(), "  "+r[6]+" ", r[6].upper()])
for r in random.sample(rows, 60):  r[5] = ""
for r in random.sample(rows, 30):  r[4] = random.choice([0, -1])
for r in random.sample(rows, 60):  r[2] = ""
rows += random.sample(rows, 120)
random.shuffle(rows)
with open(f"{out}/orders.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["order_id","order_date","customer_id","product_id","quantity","discount","region","channel"]); w.writerows(rows)
print("raw rows:", len(rows))

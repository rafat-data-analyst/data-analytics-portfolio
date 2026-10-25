"""Production-style ETL pipeline for retail sales orders.

Features
  * Incremental + idempotent: only new order_ids are loaded; re-running changes nothing.
  * Data-quality rules: bad rows are quarantined in a 'rejected' folder with a reason.
  * Audit trail: every file processed is logged in the etl_runs table and logs/etl.log.
  * Post-load validation checks and a data-quality report.

Usage
  python etl_pipeline.py            # process any new orders*.csv files in ../data/raw
  python etl_pipeline.py --reset    # delete the output database and start fresh
"""
import argparse, glob, json, logging, os, sqlite3, sys
from datetime import datetime
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FACT_COLS = ["order_id", "order_date", "customer_id", "product_id", "quantity",
             "discount", "region", "channel", "revenue", "profit"]


def load_config():
    with open(os.path.join(HERE, "config.json")) as f:
        cfg = json.load(f)
    for key in ("raw_dir", "output_dir"):
        cfg[key] = os.path.normpath(os.path.join(HERE, cfg[key]))
    return cfg


def clean_orders(raw, products, max_discount=0.5):
    """Apply data-quality rules. Returns (clean_rows, rejected_rows, discounts_filled)."""
    df = raw.copy()
    df["reject_reason"] = ""

    def reject(mask, reason):
        mask = mask & (df["reject_reason"] == "")
        df.loc[mask, "reject_reason"] = reason

    reject(df.duplicated(subset="order_id", keep="first"), "duplicate_in_batch")
    df["customer_id"] = df["customer_id"].fillna("").astype(str).str.strip()
    reject(df["customer_id"] == "", "missing_customer_id")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    reject(df["quantity"].isna() | (df["quantity"] <= 0), "invalid_quantity")
    reject(~df["product_id"].isin(products["product_id"]), "unknown_product")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    reject(df["order_date"].isna(), "invalid_date")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")
    filled = int(df.loc[df["reject_reason"] == "", "discount"].isna().sum())
    df["discount"] = df["discount"].fillna(0)
    reject((df["discount"] < 0) | (df["discount"] > max_discount), "invalid_discount")

    rejected = df[df["reject_reason"] != ""].copy()
    good = df[df["reject_reason"] == ""].drop(columns="reject_reason").copy()
    good["region"] = good["region"].astype(str).str.strip().str.title()
    good = good.merge(products, on="product_id", how="left")
    good["revenue"] = (good["quantity"] * good["unit_price"] * (1 - good["discount"])).round(2)
    good["profit"] = (good["revenue"] - good["quantity"] * good["unit_cost"]).round(2)
    good["order_date"] = good["order_date"].dt.strftime("%Y-%m-%d")
    good["quantity"] = good["quantity"].astype(int)
    return good[FACT_COLS], rejected, filled


def init_db(con):
    con.execute("""CREATE TABLE IF NOT EXISTS fact_sales (
        order_id TEXT PRIMARY KEY, order_date TEXT NOT NULL, customer_id TEXT NOT NULL,
        product_id TEXT NOT NULL, quantity INTEGER NOT NULL CHECK (quantity > 0),
        discount REAL, region TEXT, channel TEXT, revenue REAL, profit REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS etl_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT, run_ts TEXT, source_file TEXT,
        rows_in INTEGER, rows_rejected INTEGER, rows_skipped_existing INTEGER,
        rows_loaded INTEGER, status TEXT)""")
    con.commit()


def process_file(path, con, products, cfg, log):
    name = os.path.basename(path)
    raw = pd.read_csv(path, dtype=str)
    good, rejected, filled = clean_orders(raw, products, cfg["allowed_discount_max"])
    existing = {r[0] for r in con.execute("SELECT order_id FROM fact_sales")}
    new = good[~good["order_id"].isin(existing)]
    skipped = len(good) - len(new)
    new.to_sql("fact_sales", con, if_exists="append", index=False)

    rej_dir = os.path.join(cfg["output_dir"], "rejected"); os.makedirs(rej_dir, exist_ok=True)
    rej_path = os.path.join(rej_dir, f"rejected_{name}")
    if len(rejected): rejected.to_csv(rej_path, index=False)
    elif os.path.exists(rej_path): os.remove(rej_path)

    con.execute("INSERT INTO etl_runs (run_ts, source_file, rows_in, rows_rejected, rows_skipped_existing, rows_loaded, status) "
                "VALUES (?,?,?,?,?,?,?)",
                (datetime.now().isoformat(timespec="seconds"), name, len(raw), len(rejected), skipped, len(new), "SUCCESS"))
    con.commit()
    log.info("%s | in=%d rejected=%d skipped_existing=%d loaded=%d (discounts filled=%d)",
             name, len(raw), len(rejected), skipped, len(new), filled)
    if len(rejected):
        log.info("%s | reject reasons: %s", name, rejected["reject_reason"].value_counts().to_dict())


def validate(con, log):
    checks = {
        "no duplicate order_id": "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM fact_sales",
        "no negative revenue": "SELECT COUNT(*) FROM fact_sales WHERE revenue < 0",
        "no missing customer": "SELECT COUNT(*) FROM fact_sales WHERE customer_id IS NULL OR customer_id = ''",
        "no orphan products": "SELECT COUNT(*) FROM fact_sales WHERE product_id NOT IN (SELECT product_id FROM dim_products)",
    }
    for label, sql in checks.items():
        bad = con.execute(sql).fetchone()[0]
        if bad: raise ValueError(f"Validation failed: {label} ({bad} rows)")
        log.info("Validation passed: %s", label)


def write_outputs(con, cfg):
    out = cfg["output_dir"]
    for table in ("fact_sales", "dim_products", "dim_customers"):
        pd.read_sql(f"SELECT * FROM {table}", con).to_csv(os.path.join(out, f"{table}.csv"), index=False)
    runs = pd.read_sql("SELECT run_ts, source_file, rows_in, rows_rejected, rows_skipped_existing, rows_loaded, status FROM etl_runs", con)
    reasons = {}
    for p in glob.glob(os.path.join(out, "rejected", "rejected_*.csv")):
        for k, v in pd.read_csv(p)["reject_reason"].value_counts().items():
            reasons[k] = reasons.get(k, 0) + int(v)
    total = con.execute("SELECT COUNT(*), ROUND(SUM(revenue),2), ROUND(SUM(profit),2) FROM fact_sales").fetchone()
    lines = ["# Data quality report", "", f"Generated: {datetime.now():%Y-%m-%d %H:%M}", "",
             "## Current warehouse state", f"- Orders loaded: **{total[0]:,}**", f"- Total revenue: **{total[1]:,.2f}**",
             f"- Total profit: **{total[2]:,.2f}**", "", "## Run history",
             "| Time | File | Rows in | Rejected | Skipped (already loaded) | Loaded | Status |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {r.run_ts} | {r.source_file} | {r.rows_in} | {r.rows_rejected} | {r.rows_skipped_existing} | {r.rows_loaded} | {r.status} |"
              for r in runs.itertuples()]
    lines += ["", "## Rejected rows by reason"] + ([f"- {k}: {v}" for k, v in sorted(reasons.items())] or ["- none"])
    with open(os.path.join(out, "dq_report.md"), "w") as f: f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s",
                        handlers=[logging.FileHandler(os.path.join(HERE, "logs", "etl.log")), logging.StreamHandler()])
    log = logging.getLogger("etl"); cfg = load_config(); os.makedirs(cfg["output_dir"], exist_ok=True)
    db_path = os.path.join(cfg["output_dir"], cfg["db_name"])
    if args.reset and os.path.exists(db_path): os.remove(db_path); log.info("Database reset")
    files = sorted(glob.glob(os.path.join(cfg["raw_dir"], cfg["orders_pattern"])))
    if not files: log.error("No order files found in %s", cfg["raw_dir"]); sys.exit(1)
    con = sqlite3.connect(db_path); init_db(con)
    try:
        products = pd.read_csv(os.path.join(cfg["raw_dir"], "products.csv"))
        customers = pd.read_csv(os.path.join(cfg["raw_dir"], "customers.csv"))
        products.to_sql("dim_products", con, if_exists="replace", index=False)
        customers.to_sql("dim_customers", con, if_exists="replace", index=False)
        log.info("Run started: %d order file(s) found", len(files))
        for path in files: process_file(path, con, products, cfg, log)
        validate(con, log); write_outputs(con, cfg); log.info("Run finished successfully")
    except Exception:
        log.exception("Pipeline failed"); sys.exit(1)
    finally:
        con.close()


if __name__ == "__main__":
    main()

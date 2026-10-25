"""Automated tests for the cleaning rules. Run:  python -m unittest -v"""
import unittest
import pandas as pd
from etl_pipeline import clean_orders

PRODUCTS = pd.DataFrame({"product_id": ["P001"], "unit_price": [100.0], "unit_cost": [60.0]})
COLS = ["order_id","order_date","customer_id","product_id","quantity","discount","region","channel"]

def make(rows): return pd.DataFrame(rows, columns=COLS, dtype=str)
GOOD = ["O1", "2025-01-05", "C1", "P001", "2", "0.1", "dubai", "Online"]

class CleanOrdersTests(unittest.TestCase):
    def test_valid_row_passes_and_revenue_profit_calculated(self):
        good, rej, _ = clean_orders(make([GOOD]), PRODUCTS)
        self.assertEqual(len(good), 1); self.assertEqual(len(rej), 0)
        self.assertEqual(good.iloc[0]["revenue"], 180.0)   # 2 x 100 x 0.9
        self.assertEqual(good.iloc[0]["profit"], 60.0)     # 180 - 2 x 60

    def test_duplicates_in_batch_rejected(self):
        _, rej, _ = clean_orders(make([GOOD, GOOD]), PRODUCTS)
        self.assertEqual(rej["reject_reason"].tolist(), ["duplicate_in_batch"])

    def test_missing_customer_rejected(self):
        row = GOOD.copy(); row[2] = ""
        _, rej, _ = clean_orders(make([row]), PRODUCTS)
        self.assertEqual(rej.iloc[0]["reject_reason"], "missing_customer_id")

    def test_invalid_quantity_rejected(self):
        for q in ["0", "-1", "abc"]:
            row = GOOD.copy(); row[4] = q
            _, rej, _ = clean_orders(make([row]), PRODUCTS)
            self.assertEqual(rej.iloc[0]["reject_reason"], "invalid_quantity")

    def test_unknown_product_rejected(self):
        row = GOOD.copy(); row[3] = "P999"
        _, rej, _ = clean_orders(make([row]), PRODUCTS)
        self.assertEqual(rej.iloc[0]["reject_reason"], "unknown_product")

    def test_region_standardised(self):
        row = GOOD.copy(); row[6] = "  RAS AL KHAIMAH "
        good, _, _ = clean_orders(make([row]), PRODUCTS)
        self.assertEqual(good.iloc[0]["region"], "Ras Al Khaimah")

    def test_missing_discount_filled_with_zero(self):
        row = GOOD.copy(); row[5] = ""
        good, _, filled = clean_orders(make([row]), PRODUCTS)
        self.assertEqual(good.iloc[0]["discount"], 0); self.assertEqual(filled, 1)

    def test_discount_out_of_range_rejected(self):
        row = GOOD.copy(); row[5] = "0.9"
        _, rej, _ = clean_orders(make([row]), PRODUCTS)
        self.assertEqual(rej.iloc[0]["reject_reason"], "invalid_discount")

if __name__ == "__main__":
    unittest.main()

"""Runs every query in queries.sql against sales.db and writes results.md"""
import os, re, sqlite3
here = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(os.path.join(here, "..", "data", "clean", "sales.db"))
blocks = re.split(r"^-- name: ", open(os.path.join(here, "queries.sql")).read(), flags=re.M)[1:]
md = ["# SQL analysis results\n"]
for b in blocks:
    title, sql = b.split("\n", 1)
    cur = con.execute(sql); cols = [d[0] for d in cur.description]; rows = cur.fetchall()
    md += [f"## {title}\n", "```sql", sql.strip(), "```\n", "| " + " | ".join(cols) + " |", "|" + "---|"*len(cols)]
    md += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows] + [""]
open(os.path.join(here, "results.md"), "w").write("\n".join(md)); print("results.md written")

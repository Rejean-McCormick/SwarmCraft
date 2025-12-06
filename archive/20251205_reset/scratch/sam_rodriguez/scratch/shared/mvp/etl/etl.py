#!/usr/bin/env python3
"""Lightweight MVP ETL skeleton: CSV -> DuckDB in-memory, then Parquet dump"""
import csv
import sys
from pathlib import Path
try:
    import duckdb
except Exception:
    duckdb = None

DATA_DIR = Path(__file__).resolve().parents[3] / 'mvp' / 'data'
OUTPUT_DIR = Path(__file__).resolve().parents[3] / 'mvp' / 'output'


def run(csv_path: str):
    if duckdb is None:
        print("DuckDB not available. Install to run ETL.")
        return 2
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 3
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=str(OUTPUT_DIR / 'mv.db'), read_only=False)
    con.execute(f"CREATE SCHEMA IF NOT EXISTS mvp;")
    con.execute("CREATE TABLE mvp.data AS SELECT * FROM read_csv_auto(?);", [str(csv_path)])
    buff = con.execute("SELECT * FROM mvp.data LIMIT 5").fetchdf()
    print(buff.head())
    con.execute("COPY (SELECT * FROM mvp.data) TO ? (FORMAT PARQUET);", [str(OUTPUT_DIR / 'mvp.parquet')])
    con.close()
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: etl.py <path/to/input.csv>")
        sys.exit(1)
    sys.exit(run(sys.argv[1]))

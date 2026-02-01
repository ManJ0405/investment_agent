import psycopg
import os
import logging
from init_db import make_dsn
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = Path(BASE) / 'data'

def load_csv(csv_file: str):
    csv = CSV_DIR / csv_file
    
    if not csv.exists():
            raise FileNotFoundError(csv)

    with psycopg.connect(make_dsn()) as conn:
        with conn.cursor() as cur:
            with csv.open("r", encoding="utf-8") as f:
                copy_sql = """
                    COPY constituents (index_name, ticker, region)
                    FROM STDIN WITH (FORMAT csv, HEADER true)
                """
                with cur.copy(copy_sql) as copy:
                    while chunk := f.read(8192 * 1024):  
                        copy.write(chunk)
        conn.commit()
        
    print(f"Loaded {csv.name} into constituents")

if __name__ == "__main__":
    load_csv("HSI.csv")

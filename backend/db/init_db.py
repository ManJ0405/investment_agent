import psycopg
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / '.env'  # db/ → backend/ → .env
load_dotenv(dotenv_path=env_path, override=True)

def make_dsn() -> str:
     # Get .env variables
    db_name = os.getenv('db_name')
    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv('host')
    port = os.getenv('port')
    
    # print(f"  db_name  = {db_name}")
    # print(f"  user     = {user}")
    # print(f"  password = {password}")
    # print(f"  host     = {host}")
    # print(f"  port     = {port}")
    
    dsn = f"dbname={db_name} user={user} password={password} host={host} port={port}"
    
    return dsn
    

def init_table():
    BASE = os.path.dirname(os.path.abspath(__file__))
    SCHEMA_FILE = Path(BASE) / 'schema' / 'core_table.sql'

    dsn = make_dsn()
    
    # Initialize table
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            sql_text = SCHEMA_FILE.read_text(encoding="utf-8")
            for stmt in [s.strip() for s in sql_text.split(";") if s.strip()]:
                cur.execute(stmt + ";")
            logger.info("Table `constituents` created or already exists.")
            
            
init_table()
            
            


    


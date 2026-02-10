# backend/test_env.py
from dotenv import load_dotenv
import os
from pathlib import Path

# 嘗試兩種路徑寫法
load_dotenv()                           # 相對路徑
# 或明確指定
# load_dotenv(dotenv_path=Path(__file__).parent / '.env')

print("當前工作目錄:", os.getcwd())
print("POSTGRES_USER:", os.getenv("POSTGRES_USER"))
print("POSTGRES_DB  :", os.getenv("POSTGRES_DB"))
print("有沒有讀到 .env？", "有" if os.getenv("POSTGRES_USER") else "沒有")
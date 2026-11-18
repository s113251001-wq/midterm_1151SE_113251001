# db.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv  # 加入這行

# 載入 .env 檔案
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 改成從環境變數讀取，如果找不到就給一個預設值(防呆)
    conninfo = os.getenv("DATABASE_URL", "postgresql://postgres:請設定環境變數@localhost:5432/submission_system")
    
    app.state.pool = AsyncConnectionPool(
        conninfo=conninfo,
        kwargs={"row_factory": dict_row},
        open=False,
    )
    await app.state.pool.open()
    print("✅ Connected to DB")
    
    yield
    
    await app.state.pool.close()
    print("🛑 Disconnected from DB")

async def getDB(request: Request):
    async with request.app.state.pool.connection() as conn:
        yield conn
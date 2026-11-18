"""
插入兩個測試帳號。
執行方式：python seed.py
前提：已在 Adminer / psql 執行過 schema.sql（資料表必須存在）
"""

import sys
import os
import psycopg
from psycopg.rows import dict_row
import bcrypt
from dotenv import load_dotenv  # 載入環境變數套件

# 1. 載入 .env 檔案
load_dotenv()

# 2. 從環境變數讀取連線字串（這裡不再有明文密碼）
CONNINFO = os.getenv("DATABASE_URL")

# 防呆：如果沒有設定 .env，就報錯提醒
if not CONNINFO:
    print("❌ 找不到資料庫連線設定 (DATABASE_URL)。")
    print("請確認根目錄有 .env 檔案，且內容包含 DATABASE_URL=...")
    sys.exit(1)

def upsert_user(conn, username: str, password: str, role: str) -> None:
    """帳號存在就更新密碼與角色，不存在就新增（可重複執行）。"""
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed = hashed_bytes.decode('utf-8')
    
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO UPDATE
                SET password_hash = EXCLUDED.password_hash,
                    role          = EXCLUDED.role
            """,
            (username, hashed, role),
        )
    print(f"  ✓ {username:10s} role={role}")


def main() -> None:
    # 印出連線字串時，建議把密碼遮蔽，避免截圖外流（這行我幫你加了安全遮蔽）
    safe_conninfo = CONNINFO.split('@')[-1] if '@' in CONNINFO else CONNINFO
    print(f"🔌 連線至：...@{safe_conninfo}")

    try:
        with psycopg.connect(CONNINFO, row_factory=dict_row) as conn:
            # 先檢查表是否存在，避免「表不存在」的模糊錯誤
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT to_regclass('public.users') AS u"
                )
                row = cur.fetchone()

            if not row or not row["u"]:
                print("❌ 資料表不存在，請先在 Adminer 執行 schema.sql")
                sys.exit(1)

            print("📝 插入/更新測試帳號：")
            upsert_user(conn, "author1", "1234", "author")
            upsert_user(conn, "editor1", "1234", "editor")
            # with 區塊正常結束 → 自動 COMMIT

        print("✅ 完成。可用帳號：author1/1234、editor1/1234")

    except psycopg.OperationalError as e:
        print(f"❌ 無法連線資料庫：{e}")
        print("   請確認：")
        print("   1. PostgreSQL 服務已啟動")
        print("   2. .env 裡的 DATABASE_URL 密碼正確")
        print("   3. 資料庫 submission_system 已建立")
        sys.exit(1)


if __name__ == "__main__":
    main()
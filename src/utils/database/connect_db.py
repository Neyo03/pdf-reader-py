import os
import asyncpg


async def connect_db():
    conn = None
    try:
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
        )
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
    return conn
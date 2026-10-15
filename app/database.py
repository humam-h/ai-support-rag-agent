import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)
def check_database_readiness() -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM knowledge_chunks;
                """
            )
            row = cursor.fetchone()

    knowledge_chunks = row[0]

    return {
        "database": "ready",
        "knowledge_chunks": knowledge_chunks,
        "knowledge_ready": knowledge_chunks > 0,
    }
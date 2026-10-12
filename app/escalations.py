from app.database import get_connection


def create_escalation(
    subject: str,
    description: str,
    reason: str,
    idempotency_key: str,
) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO escalations (
                    subject,
                    description,
                    reason,
                    idempotency_key
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (idempotency_key)
                DO UPDATE SET
                    idempotency_key = EXCLUDED.idempotency_key
                RETURNING
                    id,
                    subject,
                    description,
                    reason,
                    status,
                    created_at,
                    idempotency_key;
                """,
                (
                    subject,
                    description,
                    reason,
                    idempotency_key,
                ),
            )

            row = cursor.fetchone()

    return {
        "id": row[0],
        "subject": row[1],
        "description": row[2],
        "reason": row[3],
        "status": row[4],
        "created_at": row[5],
        "idempotency_key": row[6],
    }
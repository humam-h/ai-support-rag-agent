from app.database import get_connection


def create_escalation(
    subject: str,
    description: str,
    reason: str,
) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO escalations (
                    subject,
                    description,
                    reason
                )
                VALUES (%s, %s, %s)
                RETURNING
                    id,
                    subject,
                    description,
                    reason,
                    status,
                    created_at;
                """,
                (
                    subject,
                    description,
                    reason,
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
    }
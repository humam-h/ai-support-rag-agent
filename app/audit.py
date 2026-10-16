import json

from app.database import get_connection
import logging


logger = logging.getLogger(__name__)


def create_audit_event(
    request_id: str,
    event_type: str,
    outcome: str,
    details: dict | None = None,
) -> dict:
    if details is None:
        details = {}

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agent_audit_events (
                    request_id,
                    event_type,
                    outcome,
                    details
                )
                VALUES (%s, %s, %s, %s::jsonb)
                RETURNING
                    id,
                    request_id,
                    event_type,
                    outcome,
                    details,
                    created_at;
                """,
                (
                    request_id,
                    event_type,
                    outcome,
                    json.dumps(details),
                ),
            )

            row = cursor.fetchone()

    return {
        "id": row[0],
        "request_id": row[1],
        "event_type": row[2],
        "outcome": row[3],
        "details": row[4],
        "created_at": row[5],
    }
def record_audit_event(
    request_id: str,
    event_type: str,
    outcome: str,
    details: dict | None = None,
) -> bool:
    try:
        create_audit_event(
            request_id=request_id,
            event_type=event_type,
            outcome=outcome,
            details=details,
        )
        return True

    except Exception:
        logger.exception("Failed to record audit event")
        return False
        
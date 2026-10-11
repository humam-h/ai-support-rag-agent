from app.database import get_connection
from app.embeddings import embed_text


def search_knowledge(query, top_k=3, min_score=0.30):
    query_embedding = embed_text(query)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    source,
                    chunk_index,
                    text,
                    1 - (embedding <=> %s::vector) AS score
                FROM knowledge_chunks
                WHERE 1 - (embedding <=> %s::vector) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding,
                    query_embedding,
                    min_score,
                    query_embedding,
                    top_k,
                ),
            )

            rows = cursor.fetchall()

    results = []

    for row in rows:
        results.append(
            {
                "source": row[0],
                "chunk_index": row[1],
                "text": row[2],
                "score": float(row[3]),
            }
        )

    return results

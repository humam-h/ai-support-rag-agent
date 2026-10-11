from app.database import get_connection
from app.embeddings import embed_text
from app.knowledge import load_documents, chunk_documents


def ingest_knowledge():
    documents = load_documents()
    chunks = chunk_documents(documents)

    with get_connection() as conn:
        with conn.cursor() as cursor:

            for chunk in chunks:
                embedding = embed_text(chunk["text"])

                cursor.execute(
                    """
                    INSERT INTO knowledge_chunks (
                        source,
                        chunk_index,
                        text,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source, chunk_index)
                    DO UPDATE SET
                        text = EXCLUDED.text,
                        embedding = EXCLUDED.embedding;
                    """,
                    (
                        chunk["source"],
                        chunk["chunk_index"],
                        chunk["text"],
                        embedding,
                    ),
                )

                print(
                    "Ingested:",
                    chunk["source"],
                    "chunk",
                    chunk["chunk_index"],
                )


if __name__ == "__main__":
    ingest_knowledge()

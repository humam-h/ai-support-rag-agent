import numpy as np

from app.embeddings import embed_text
from app.knowledge import load_documents, chunk_documents


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def build_index():
    documents = load_documents()
    chunks = chunk_documents(documents)

    indexed_chunks = []

    for chunk in chunks:
        embedding = embed_text(chunk["text"])

        indexed_chunks.append(
            {
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "embedding": embedding,
            }
        )

    return indexed_chunks


def search(
    query,
    indexed_chunks,
    top_k=3,
    min_score=0.30,
):
    query_embedding = embed_text(query)

    results = []

    for chunk in indexed_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        if score >= min_score:
            results.append(
                {
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "score": float(score),
                }
            )

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]
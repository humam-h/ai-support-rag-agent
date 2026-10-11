from pathlib import Path


KNOWLEDGE_DIR = Path("knowledge")


def load_documents():
    documents = []

    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        documents.append(
            {
                "source": path.name,
                "text": text,
            }
        )

    return documents


def chunk_documents(documents, chunk_size=500):
    chunks = []

    for document in documents:
        source = document["source"]

        paragraphs = [
            paragraph.strip()
            for paragraph in document["text"].split("\n\n")
            if paragraph.strip()
        ]

        current_chunk = []
        current_length = 0
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)

            if (
                current_chunk
                and current_length + paragraph_length > chunk_size
            ):
                chunks.append(
                    {
                        "source": source,
                        "chunk_index": chunk_index,
                        "text": "\n\n".join(current_chunk),
                    }
                )

                chunk_index += 1
                current_chunk = []
                current_length = 0

            current_chunk.append(paragraph)
            current_length += paragraph_length

        if current_chunk:
            chunks.append(
                {
                    "source": source,
                    "chunk_index": chunk_index,
                    "text": "\n\n".join(current_chunk),
                }
            )

    return chunks
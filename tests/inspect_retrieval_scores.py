from app.vector_store import search_knowledge


queries = [
    "My printer displays error 49 and will not print.",
    (
        "printer displays error 49 will not print "
        "error 49 troubleshooting"
    ),
]

for query in queries:
    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)

    results = search_knowledge(
        query=query,
        top_k=3,
        min_score=-1.0,
    )

    print("\nTOP MATCHES:")

    for result in results:
        print(
            f"{result['score']:.4f} | "
            f"{result['source']} | "
            f"chunk {result['chunk_index']}"
        )

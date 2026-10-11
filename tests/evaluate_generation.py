from app.evaluator import evaluate_grounding
from app.rag import generate_answer


TEST_CASES = [
    {
        "name": "VPN hostname failure",
        "query": (
            "Subject: VPN connected but servers unavailable\n\n"
            "Description:\n"
            "My VPN says connected, but I cannot reach "
            "company servers by their names."
        ),
    },
    {
        "name": "VPN authentication failure",
        "query": (
            "Subject: VPN login problem\n\n"
            "Description:\n"
            "The VPN rejects my login and MFA is not working."
        ),
    },
    {
        "name": "Password reset",
        "query": (
            "Subject: Password reset\n\n"
            "Description:\n"
            "I forgot my account password and need it reset."
        ),
    },
    {
        "name": "Repeated account lockout",
        "query": (
            "Subject: Account keeps locking\n\n"
            "Description:\n"
            "My account keeps locking after I change my password."
        ),
    },
]


def evaluate():
    for test in TEST_CASES:
        result = generate_answer(test["query"])

        print("\n" + "=" * 70)
        print("TEST:", test["name"])
        print("STATUS:", result["status"])

        print("\nRETRIEVED:")
        for chunk in result["retrieved_chunks"]:
            print(
                round(chunk["score"], 4),
                chunk["source"],
                chunk["chunk_index"],
            )

        print("\nANSWER:")
        print(result["answer"])

        evaluation = evaluate_grounding(
            query=test["query"],
            answer=result["answer"],
            retrieved_chunks=result["retrieved_chunks"],
        )

        print("\nGROUNDING EVALUATION:")
        print(evaluation)


if __name__ == "__main__":
    evaluate()

from app.vector_store import search_knowledge


TEST_CASES = [
    # Known-answer questions
    {
        "query": "My VPN connects but internal hostnames do not work.",
        "expected_source": "vpn-troubleshooting.md",
    },
    {
        "query": "The VPN rejects my login and MFA is not working.",
        "expected_source": "vpn-troubleshooting.md",
    },
    {
        "query": "My laptop connects to Wi-Fi but does not receive a valid IP address.",
        "expected_source": "wifi-troubleshooting.md",
    },
    {
        "query": "Several employees suddenly cannot connect to the wireless network.",
        "expected_source": "wifi-troubleshooting.md",
    },
    {
        "query": "I forgot my account password and need it reset.",
        "expected_source": "password-reset.md",
    },
    {
        "query": "My account keeps locking after I change my password.",
        "expected_source": "password-reset.md",
    },

    # Unknown-answer questions
    {
        "query": "The office printer displays error 49.",
        "expected_source": None,
    },
    {
        "query": "Outlook crashes every time I open my mailbox.",
        "expected_source": None,
    },
    {
        "query": "My laptop hard drive is making clicking noises.",
        "expected_source": None,
    },
    {
        "query": "Microsoft Teams cannot detect my webcam.",
        "expected_source": None,
    },
]


def evaluate():
    

    passed = 0

    for test in TEST_CASES:
        query = test["query"]
        expected_source = test["expected_source"]

        results = search_knowledge(query)

        actual_source = (
            results[0]["source"]
            if results
            else None
        )

        success = actual_source == expected_source

        if success:
            passed += 1

        print("\n" + "=" * 70)
        print("Query:", query)
        print("Expected:", expected_source)
        print("Actual:", actual_source)
        print("Result:", "PASS" if success else "FAIL")

        if results:
            print("Top score:", round(results[0]["score"], 4))
        else:
            print("Top score: No result")

    print("\n" + "=" * 70)
    print(f"Passed: {passed}/{len(TEST_CASES)}")
    print(
        f"Accuracy: {passed / len(TEST_CASES) * 100:.1f}%"
    )


if __name__ == "__main__":
    evaluate()

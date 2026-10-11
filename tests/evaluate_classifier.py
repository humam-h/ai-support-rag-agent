from app.classifier import determine_disposition


TEST_CASES = [
    "My VPN connects but internal hostnames do not work.",
    "Please reset my password.",
    "My account is locked. Please unlock it.",
    "How do I troubleshoot repeated account lockouts?",
    "My MFA is not working. What should I check?",
    "Please change my MFA method.",
]


def evaluate():
    for query in TEST_CASES:
        result = determine_disposition(query)

        print("\nREQUEST:")
        print(query)

        print("REQUIRED CAPABILITY:")
        print(result["required_capability"])

        print("STATUS:")
        print(result["status"])


if __name__ == "__main__":
    evaluate()

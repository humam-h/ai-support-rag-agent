from app.agent import run_agent


query = (
    "My VPN connects, but I cannot access "
    "internal servers by hostname. What should I check?"
)

print("USER QUERY:")
print(query)

result = run_agent(query)

print("\nAGENT STATUS:")
print(result["status"])

print("\nAGENT ITERATIONS:")
print(result["iterations"])

print("\nAGENT ANSWER:")
print(result["answer"])
from agent import run_agent

print("=" * 50)
print("  Free AI Agent — Groq + Llama 3.3 (FREE)")
print("  Type 'quit' to exit")
print("=" * 50)

while True:
    user = input("\nYou: ").strip()
    if not user:
        continue
    if user.lower() in ["quit", "q", "exit"]:
        print("Bye!")
        break
    answer = run_agent(user)
    print(f"\nAgent: {answer}")

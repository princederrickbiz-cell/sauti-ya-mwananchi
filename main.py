"""
Sauti ya Mwananchi

Run modes:
  python main.py            -> start the FastAPI webhook server
  python main.py --test     -> interactive CLI for local testing
  python main.py --demo     -> run canned demo queries for judges
"""
import sys
import os


def run_server():
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    print("Starting Sauti ya Mwananchi webhook server...")
    uvicorn.run("api.webhook:app", host="0.0.0.0", port=port, reload=False)


def run_interactive():
    from agents.msaidizi import route

    print("\nSauti ya Mwananchi - Interactive Test Mode")
    print("Type your message, or type 'exit' to quit.\n")
    phone = "+254700000000"

    while True:
        try:
            msg = input("You: ").strip()
            if msg.lower() in ("exit", "quit"):
                break
            if not msg:
                continue

            reply = route(phone=phone, message=msg)
            print(f"\nMsaidizi: {reply}\n")
        except KeyboardInterrupt:
            break


def run_demo():
    from agents.msaidizi import route
    from agents.ukweli import check
    from agents.mwenza import handle_ussd

    demo_queries = [
        "Hello! What is Sauti ya Mwananchi?",
        "Wapi nipigie kura Westlands?",
        "Is it true that you need a party card to vote?",
        "Ni haki gani ninazopata siku ya uchaguzi?",
        "Mambo, niaje kupiga kura first time?",
        "What happens if my name is not on the register?",
    ]

    print("\n" + "=" * 60)
    print("SAUTI YA MWANANCHI - DEMO RUN")
    print("=" * 60)

    phone = "+254711111111"
    for query in demo_queries:
        print(f"\nUser: {query}")
        reply = route(phone=phone, message=query)
        print(f"Agent: {reply}")
        print("-" * 40)

    print("\nUSSD DEMO (Mwenza)")
    print(handle_ussd("sess001", "+254722222222", ""))
    print("\n> User presses 3")
    print(handle_ussd("sess001", "+254722222222", "3"))

    print("\nFACT-CHECK DEMO (Ukweli)")
    for claim in [
        "You need a party card to vote",
        "Voting is compulsory in Kenya",
        "Results are only announced on TV",
    ]:
        print(f"\nClaim: {claim}")
        print(check(claim, lang="en"))
        print("-" * 40)


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_interactive()
    elif "--demo" in sys.argv:
        run_demo()
    else:
        run_server()

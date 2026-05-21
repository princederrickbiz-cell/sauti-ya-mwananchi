SESSIONS = {}


MENU = """CON Sauti ya Mwananchi
1. My voting rights
2. Check a claim
3. How voting works
4. Polling station help"""


def handle_ussd(session_id, phone, text):
    # Store only temporary menu state. Never store ID numbers or voter-card details.
    SESSIONS.setdefault(session_id, {"phone": phone})
    parts = [part for part in text.split("*") if part]

    if not parts:
        return MENU

    choice = parts[0]
    if choice == "1":
        return (
            "END You have the right to register and vote by secret ballot. "
            "Source: Constitution of Kenya, Article 38."
        )
    if choice == "2":
        return (
            "END Send the claim by SMS/WhatsApp to Sauti ya Mwananchi. "
            "We will mark unsupported claims as Unverified."
        )
    if choice == "3":
        return (
            "END On election day, confirm your station, join the queue, identify yourself "
            "to officials, mark your ballot secretly, and place it in the ballot box."
        )
    if choice == "4":
        return (
            "END Use official IEBC channels to confirm your polling station. "
            "Do not share your ID number in this demo."
        )

    return "END Invalid choice. Please dial again."

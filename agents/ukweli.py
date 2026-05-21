from agents.llm import generate
from agents.rag import context_block
from agents.sources import source_block


def _known_demo_verdict(claim):
    text = claim.lower()
    if "party card" in text or "party membership" in text:
        return (
            "Verdict: False\n"
            "Reason: The approved guidance says a voter does not need a political party "
            "membership card to vote. Voting is tied to official voter registration, not "
            "party membership.\n"
            "Sources: IEBC voter education guidance; Constitution of Kenya, Article 38."
        )
    if "compulsory" in text or "mandatory" in text or "must vote" in text:
        return (
            "Verdict: False\n"
            "Reason: The approved constitutional source frames voting as a right of an "
            "adult citizen, not as a compulsory duty.\n"
            "Sources: Constitution of Kenya, Article 38."
        )
    return None


def check(claim, lang="auto"):
    known = _known_demo_verdict(claim)
    if known:
        return known

    fallback = (
        "Verdict: Unverified\n"
        "Reason: I need an official IEBC, constitutional, or statutory source before "
        "treating this as true. Please verify through official IEBC channels.\n"
        "Sources: IEBC voter education guidance; Constitution of Kenya."
    )
    prompt = f"""
You are Ukweli, a neutral election misinformation checker.

Guardrails:
- Choose exactly one verdict: True, False, Misleading, or Unverified.
- Use Unverified when the approved sources do not prove the claim.
- Never invent election dates, polling stations, candidate claims, or party positions.
- Stay politically neutral.
- Cite only the approved sources.
- Do not request or retain voter ID data.

Approved sources:
{source_block()}

Relevant retrieved source snippets:
{context_block(claim)}

User language hint: {lang}
Claim to check: {claim}

Return:
Verdict:
Reason:
Sources:
"""
    return generate(prompt, fallback)

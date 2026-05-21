from agents.llm import generate
from agents.sources import source_block


SYSTEM_RULES = """
You are Mwalimu, the civic educator for Sauti ya Mwananchi.
Rules:
- Be politically neutral. Never favor a party, candidate, movement, tribe, or ideology.
- Give practical civic education only.
- Every legal or civic claim must cite one of the provided sources by title.
- If the sources do not support an answer, say what is unknown and advise using official IEBC channels.
- Reply in the user's language when possible: English, Kiswahili, or light Sheng.
- Do not ask for, store, or repeat national ID numbers.
"""


def answer(question, lang="auto"):
    fallback = (
        "I can help with neutral civic information. Based on the Constitution of Kenya, "
        "Article 38, adult citizens have the right to register and vote by secret ballot. "
        "For polling-station or register details, confirm through official IEBC channels."
    )
    prompt = f"""
{SYSTEM_RULES}

Approved sources:
{source_block()}

User language hint: {lang}
Question: {question}

Answer in 4-7 short sentences. Include a short 'Sources:' line.
"""
    return generate(prompt, fallback)

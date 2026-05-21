from agents import kiongozi, mwalimu, ukweli


FACT_WORDS = [
    "true",
    "false",
    "rumour",
    "rumor",
    "claim",
    "fact",
    "ukweli",
    "is it",
    "is voting",
    "compulsory",
    "mandatory",
    "party card",
    "party membership",
]
LOCATION_WORDS = [
    "where",
    "polling",
    "station",
    "vote at",
    "wapi",
    "kura wapi",
    "nipigie kura",
]


def _detect_language(message):
    text = message.lower()
    sw_words = ["wapi", "kura", "haki", "ni", "nini", "kupiga", "siku"]
    sheng_words = ["mambo", "niaje", "rada", "maze", "form"]
    if any(word in text for word in sheng_words):
        return "sheng"
    if any(word in text for word in sw_words):
        return "sw"
    return "en"


def _intent(message):
    text = message.lower()
    if any(word in text for word in FACT_WORDS):
        return "fact_check"
    if any(word in text for word in LOCATION_WORDS):
        return "locator"
    return "education"


def route(phone, message):
    lang = _detect_language(message)
    intent = _intent(message)

    if intent == "fact_check":
        return ukweli.check(message, lang=lang)
    if intent == "locator":
        return kiongozi.locate(message)
    return mwalimu.answer(message, lang=lang)

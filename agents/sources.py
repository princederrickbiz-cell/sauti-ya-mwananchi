CIVIC_SOURCES = [
    {
        "id": "constitution-article-38",
        "title": "Constitution of Kenya, Article 38",
        "text": (
            "Every adult citizen has the right to be registered as a voter, "
            "to vote by secret ballot, and to be a candidate for public office."
        ),
    },
    {
        "id": "constitution-article-81",
        "title": "Constitution of Kenya, Article 81",
        "text": (
            "Kenya's electoral system must follow principles including free and fair "
            "elections, universal suffrage, equality of vote, and voting by secret ballot."
        ),
    },
    {
        "id": "constitution-article-86",
        "title": "Constitution of Kenya, Article 86",
        "text": (
            "The electoral body must ensure voting is simple, accurate, verifiable, "
            "secure, accountable, and transparent."
        ),
    },
    {
        "id": "iebc-voter-education",
        "title": "IEBC voter education guidance",
        "text": (
            "A voter should confirm their registration details and polling station "
            "through official IEBC channels. A voter does not need a political party "
            "membership card to vote. Assistance at polling stations must not compromise "
            "the secrecy of the vote."
        ),
    },
    {
        "id": "elections-act-voter-register",
        "title": "Elections Act voter register provisions",
        "text": (
            "Voting depends on registration in the official register of voters. A person "
            "whose name is missing should seek help through official IEBC channels."
        ),
    },
]


def source_block():
    lines = []
    for source in CIVIC_SOURCES:
        lines.append(f"- {source['title']} ({source['id']}): {source['text']}")
    return "\n".join(lines)

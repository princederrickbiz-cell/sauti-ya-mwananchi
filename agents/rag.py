import re
from functools import lru_cache

from agents.settings import ROOT_DIR
from agents.sources import CIVIC_SOURCES


DOCS_DIR = ROOT_DIR / "docs"
SUPPORTED_SUFFIXES = {".md", ".txt"}
STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "from",
    "what",
    "when",
    "where",
    "wapi",
    "kura",
    "haki",
    "voter",
    "vote",
    "voting",
}


def _tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOP_WORDS
    }


def _chunks(text, size=900, overlap=140):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


@lru_cache(maxsize=1)
def load_index():
    records = []

    for source in CIVIC_SOURCES:
        records.append(
            {
                "title": source["title"],
                "source": source["id"],
                "text": source["text"],
                "tokens": _tokens(source["text"] + " " + source["title"]),
            }
        )

    if DOCS_DIR.exists():
        for path in sorted(DOCS_DIR.rglob("*")):
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for index, chunk in enumerate(_chunks(text), start=1):
                records.append(
                    {
                        "title": f"{path.name} chunk {index}",
                        "source": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
                        "text": chunk,
                        "tokens": _tokens(chunk),
                    }
                )

    return records


def retrieve(query, limit=6):
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    scored = []
    for record in load_index():
        score = len(query_tokens & record["tokens"])
        if score:
            scored.append((score, record))

    scored.sort(key=lambda item: (-item[0], item[1]["source"], item[1]["title"]))
    return [record for _, record in scored[:limit]]


def context_block(query, limit=6):
    records = retrieve(query, limit=limit)
    if not records:
        return "No matching trusted source snippets were found."

    lines = []
    for record in records:
        lines.append(f"- {record['title']} [{record['source']}]: {record['text']}")
    return "\n".join(lines)

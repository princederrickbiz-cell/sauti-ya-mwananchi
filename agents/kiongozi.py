import csv
import json
import re

from agents.settings import ROOT_DIR


CSV_DATA_PATH = ROOT_DIR / "data" / "polling_stations.csv"
JSON_DATA_PATH = ROOT_DIR / "data" / "polling_stations.json"


REQUIRED_COLUMNS = ["county", "constituency", "ward", "station"]
STOP_WORDS = {
    "where",
    "vote",
    "voting",
    "polling",
    "station",
    "centre",
    "center",
    "registration",
    "wapi",
    "kura",
    "kupiga",
    "nipige",
    "nipigie",
    "naweza",
    "tafuta",
    "find",
    "my",
    "the",
    "kwa",
}


def _load_stations():
    if CSV_DATA_PATH.exists():
        with CSV_DATA_PATH.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
            if missing:
                raise ValueError(
                    "data/polling_stations.csv is missing required columns: "
                    + ", ".join(missing)
                )
            return [
                {key: (value or "").strip() for key, value in row.items()}
                for row in reader
                if any((row.get(column) or "").strip() for column in REQUIRED_COLUMNS)
            ]

    if JSON_DATA_PATH.exists():
        return json.loads(JSON_DATA_PATH.read_text(encoding="utf-8"))

    return []


def _supported_areas(stations):
    areas = sorted(
        {
            f"{station['constituency']} - {station['ward']}"
            for station in stations
            if station.get("constituency") and station.get("ward")
        }
    )
    return ", ".join(areas[:6])


def locate(query):
    stations = _load_stations()
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", query.lower())
        if len(token) > 2 and token not in STOP_WORDS
    ]
    matches = []

    if not tokens:
        return (
            "Tell me a county, constituency, ward, or centre name to search. "
            "For example: 'Kangemi', 'Limuru', or 'Westlands'. "
            "Do not share your ID number here."
        )

    for station in stations:
        county = station.get("county", "").lower()
        constituency = station.get("constituency", "").lower()
        ward = station.get("ward", "").lower()
        station_name = station.get("station", "").lower()

        score = 0
        for token in tokens:
            if token == constituency:
                score += 100
            elif token == ward:
                score += 90
            elif token == county:
                score += 60
            elif token in constituency.split():
                score += 55
            elif token in ward.split():
                score += 45
            elif token in station_name.split():
                score += 35
            elif token in constituency:
                score += 20
            elif token in ward:
                score += 16
            elif token in station_name:
                score += 8
            elif token in county:
                score += 6

        if score > 0:
            matches.append((score, station))

    if not matches:
        areas = _supported_areas(stations)
        supported = (
            f"This demo currently has sample entries for: {areas}. "
            if areas
            else "No registration-centre dataset has been loaded yet. "
        )
        return (
            "I cannot confirm your exact IEBC registration or polling centre from the available dataset. "
            f"{supported}"
            "Try a constituency or ward name, for example 'Westlands' or 'Umoja'. "
            "For your final official polling station, check IEBC channels. "
            "Do not share your ID number here."
        )

    matches.sort(
        key=lambda item: (
            -item[0],
            item[1].get("county", ""),
            item[1].get("constituency", ""),
            item[1].get("ward", ""),
            item[1].get("station", ""),
        )
    )
    top = [station for _, station in matches[:3]]
    lines = ["Possible IEBC registration/polling centre matches from the available dataset:"]
    for station in top:
        source = station.get("source", "dataset")
        source_date = station.get("source_date", "")
        source_text = f" Source: {source}{f' ({source_date})' if source_date else ''}."
        lines.append(
            f"- {station['station']}, {station['ward']} Ward, "
            f"{station['constituency']}, {station['county']}."
            f"{source_text}"
        )
    lines.append(
        "Confirm your final official polling station through IEBC before election day. "
        "Do not share your ID number here."
    )
    return "\n".join(lines)

import argparse
import csv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "data" / "polling_stations.csv"


COLUMN_ALIASES = {
    "county": ["county", "county_name", "county name"],
    "constituency": ["constituency", "constituency_name", "constituency name"],
    "ward": ["ward", "ward_name", "ward name"],
    "station": [
        "station",
        "polling_station",
        "polling station",
        "polling_centre",
        "polling centre",
        "registration_centre",
        "registration centre",
        "centre",
        "center",
    ],
}


def _normalize_header(value):
    return " ".join((value or "").strip().lower().replace("_", " ").split())


def _find_column(headers, canonical_name):
    normalized = {_normalize_header(header): header for header in headers}
    for alias in COLUMN_ALIASES[canonical_name]:
        match = normalized.get(_normalize_header(alias))
        if match:
            return match
    return None


def _clean(value):
    return " ".join((value or "").strip().split())


def import_csv(input_path, source, source_date):
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("The input CSV has no header row.")

        mapping = {
            name: _find_column(reader.fieldnames, name)
            for name in ["county", "constituency", "ward", "station"]
        }
        missing = [name for name, column in mapping.items() if not column]
        if missing:
            raise ValueError(
                "Could not find required columns in the input CSV: "
                + ", ".join(missing)
                + "\nExpected something like county, constituency, ward, polling_station."
            )

        rows = []
        seen = set()
        for row in reader:
            normalized = {
                "county": _clean(row.get(mapping["county"])),
                "constituency": _clean(row.get(mapping["constituency"])),
                "ward": _clean(row.get(mapping["ward"])),
                "station": _clean(row.get(mapping["station"])),
                "source": source,
                "source_date": source_date,
            }
            if not all(normalized[key] for key in ["county", "constituency", "ward", "station"]):
                continue

            key = (
                normalized["county"].lower(),
                normalized["constituency"].lower(),
                normalized["ward"].lower(),
                normalized["station"].lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(normalized)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["county", "constituency", "ward", "station", "source", "source_date"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Normalize an official IEBC polling-station CSV for Kiongozi."
    )
    parser.add_argument("input_csv", help="Path to the downloaded/converted IEBC CSV file.")
    parser.add_argument("--source", default="IEBC", help="Source label to store in the dataset.")
    parser.add_argument(
        "--source-date",
        default="",
        help="Publication or download date, for example 2026-05-21.",
    )
    args = parser.parse_args()

    count = import_csv(args.input_csv, args.source, args.source_date)
    print(f"Imported {count} polling-station rows into {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

import argparse
import csv
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests
from requests import RequestException


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "data" / "polling_stations.csv"
BASE_URL = "https://www.iebc.or.ke/registration/"


class OptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.options = []
        self._in_option = False
        self._value = ""
        self._label_parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "option":
            self._in_option = True
            self._label_parts = []
            self._value = ""
            for name, value in attrs:
                if name.lower() == "value":
                    self._value = value or ""

    def handle_data(self, data):
        if self._in_option:
            self._label_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "option" and self._in_option:
            label = " ".join("".join(self._label_parts).split())
            value = self._value.strip()
            if value and label and "select" not in label.lower():
                self.options.append({"value": value, "label": label})
            self._in_option = False


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._in_cell = False
        self._in_script = False
        self._in_style = False
        self._current_cell = []
        self._current_row = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self._in_script = True
        if tag.lower() == "style":
            self._in_style = True
        if tag.lower() == "tr":
            self._current_row = []
        if tag.lower() in ("td", "th"):
            self._in_cell = True
            self._current_cell = []

    def handle_data(self, data):
        if self._in_cell and not self._in_script and not self._in_style:
            self._current_cell.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script":
            self._in_script = False
        if tag.lower() == "style":
            self._in_style = False
        if tag.lower() in ("td", "th") and self._in_cell:
            text = " ".join("".join(self._current_cell).split())
            self._current_row.append(text)
            self._in_cell = False
        if tag.lower() == "tr" and self._current_row:
            self.rows.append(self._current_row)


def clean(value):
    return " ".join((value or "").strip().split())


def snippet_around(text, needle, size=700):
    index = text.find(needle)
    if index == -1:
        return text[:size]
    start = max(index - 150, 0)
    end = min(index + size, len(text))
    return text[start:end]


def option_list(html):
    parser = OptionParser()
    parser.feed(html)
    return parser.options


def station_names(html):
    parser = TableParser()
    parser.feed(html)
    names = []
    for row in parser.rows:
        if len(row) != 1:
            continue
        for cell in row:
            text = clean(cell)
            if not text:
                continue
            lower = text.lower()
            if lower in {"polling station names", "registration centre names"}:
                continue
            if "show" in lower and "entries" in lower:
                continue
            if lower.startswith("here are"):
                continue
            if lower.startswith("$(") or "function" in lower or "-->" in lower:
                continue
            names.append(text)

    return names


FIELDNAMES = ["county", "constituency", "ward", "station", "source", "source_date"]


def request_with_retry(method, session, url, retries, retry_delay, **kwargs):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = getattr(session, method)(url, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as exc:
            last_error = exc
            if attempt == retries:
                break
            wait = retry_delay * attempt
            print(f"Request failed ({exc}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
    raise last_error


def post(session, endpoint, data, delay, verify_tls, retries, retry_delay):
    time.sleep(delay)
    response = request_with_retry(
        "post",
        session,
        urljoin(BASE_URL, endpoint),
        retries,
        retry_delay,
        data=data,
        timeout=30,
        verify=verify_tls,
    )
    response.raise_for_status()
    return response.text


def load_existing_keys(output_path):
    output_path = Path(output_path)
    if not output_path.exists():
        return set()

    with output_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return {
            (
                clean(row.get("county")).lower(),
                clean(row.get("constituency")).lower(),
                clean(row.get("ward")).lower(),
                clean(row.get("station")).lower(),
            )
            for row in reader
        }


def append_rows(rows, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = output_path.exists() and output_path.stat().st_size > 0
    with output_path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def fetch_centres(
    limit_county=None,
    limit_constituency=None,
    delay=0.25,
    verify_tls=True,
    debug=False,
    output_path=None,
    resume=False,
    retries=3,
    retry_delay=2.0,
    continue_on_error=False,
):
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "SautiYaMwananchi/0.1 civic demo contact: local-development",
            "Referer": BASE_URL + "?where",
        }
    )

    page = request_with_retry(
        "get",
        session,
        BASE_URL + "?where",
        retries,
        retry_delay,
        timeout=30,
        verify=verify_tls,
    )
    counties = option_list(page.text)
    if debug:
        print(f"Found {len(counties)} counties")
        print("County sample:", ", ".join(county["label"] for county in counties[:8]))
    rows = []
    seen = load_existing_keys(output_path) if resume and output_path else set()

    for county in counties:
        county_label = clean(county["label"])
        if limit_county and limit_county.lower() not in county_label.lower():
            continue

        const_html = post(
            session,
            "show_const.php",
            {
                "cid": county["value"],
                "county": county["value"],
            },
            delay,
            verify_tls,
            retries,
            retry_delay,
        )
        constituencies = option_list(const_html)
        if debug:
            print(f"{county_label}: found {len(constituencies)} constituencies")
            if not constituencies:
                print("Constituency response sample:")
                print(const_html[:500])

        for constituency in constituencies:
            constituency_label = clean(constituency["label"])
            if limit_constituency and limit_constituency.lower() not in constituency_label.lower():
                continue

            ward_html = post(
                session,
                "show_wards.php",
                {
                    "ccid": constituency["value"],
                    "county": county["value"],
                    "const": constituency["value"],
                    "constituency": constituency["value"],
                },
                delay,
                verify_tls,
                retries,
                retry_delay,
            )
            wards = option_list(ward_html)
            if debug:
                print(f"{county_label} / {constituency_label}: found {len(wards)} wards")
                print("Ward response show_stations snippet:")
                print(snippet_around(ward_html, "show_stations"))
                if not wards:
                    print("Ward response sample:")
                    print(ward_html[:500])

            for ward in wards:
                ward_label = clean(ward["label"])
                try:
                    stations_html = post(
                        session,
                        "show_stations.php",
                        {
                            "wardid": ward["value"],
                            "wid": ward["value"],
                            "county": county["value"],
                            "const": constituency["value"],
                            "constituency": constituency["value"],
                            "ward": ward["value"],
                        },
                        delay,
                        verify_tls,
                        retries,
                        retry_delay,
                    )
                except RequestException as exc:
                    if continue_on_error:
                        print(
                            f"Skipping {county_label} / {constituency_label} / {ward_label} "
                            f"after repeated failures: {exc}"
                        )
                        continue
                    raise

                stations = station_names(stations_html)
                if debug:
                    print(
                        f"{county_label} / {constituency_label} / {ward_label}: "
                        f"found {len(stations)} stations"
                    )
                    if not stations:
                        print("Station response sample:")
                        print(stations_html[:500])
                ward_rows = []
                for station in stations:
                    row = {
                        "county": county_label,
                        "constituency": constituency_label,
                        "ward": ward_label,
                        "station": station,
                        "source": "IEBC registration centres page",
                        "source_date": time.strftime("%Y-%m-%d"),
                    }
                    key = (
                        row["county"].lower(),
                        row["constituency"].lower(),
                        row["ward"].lower(),
                        row["station"].lower(),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(row)
                    ward_rows.append(row)

                if output_path and ward_rows:
                    append_rows(ward_rows, output_path)
                print(f"{county_label} / {constituency_label} / {ward_label}: {len(rows)} total")

    return rows


def write_csv(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch public IEBC registration centre data into polling_stations.csv."
    )
    parser.add_argument("--county", help="Fetch one county first, for example NAIROBI.")
    parser.add_argument("--constituency", help="Optional constituency filter, for example WESTLANDS.")
    parser.add_argument("--delay", type=float, default=0.25, help="Delay between requests in seconds.")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output CSV path.")
    parser.add_argument("--debug", action="store_true", help="Print response counts and samples.")
    parser.add_argument("--resume", action="store_true", help="Append only rows not already in the output CSV.")
    parser.add_argument("--retries", type=int, default=5, help="Number of retries per request.")
    parser.add_argument("--retry-delay", type=float, default=3.0, help="Base retry delay in seconds.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Skip a ward after repeated request failures and keep fetching.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow writing an empty CSV if no rows are fetched.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification if your local Python cannot verify IEBC's certificate.",
    )
    args = parser.parse_args()

    rows = fetch_centres(
        limit_county=args.county,
        limit_constituency=args.constituency,
        delay=args.delay,
        verify_tls=not args.insecure,
        debug=args.debug,
        output_path=args.output,
        resume=args.resume,
        retries=args.retries,
        retry_delay=args.retry_delay,
        continue_on_error=args.continue_on_error,
    )
    if not rows and not args.allow_empty and not args.resume:
        raise SystemExit(
            "Fetched 0 rows, so the existing dataset was not overwritten. "
            "Run again with --debug to inspect the IEBC responses."
        )
    output_path = Path(args.output)
    if args.resume:
        print(f"Appended {len(rows)} new rows to {output_path}")
    else:
        write_csv(rows, output_path)
        print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()

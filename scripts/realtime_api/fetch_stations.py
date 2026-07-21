#!/usr/bin/env python3
"""Fetch all stations from the sea-level API, excluding Australia and
New Zealand, and write the result to stations.json in this directory.
"""
import json
import os
import ssl
import urllib.request

API_URL = "https://sea-level-dev.cosppac.cloud/api/stations/"
EXCLUDED_COUNTRIES = {"Australia", "New Zealand"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(BASE_DIR, "stations.json")


def fetch_stations():
    # The endpoint's certificate chain doesn't validate locally, so use an
    # unverified SSL context to fetch it.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    stations = fetch_stations()
    total = len(stations)

    filtered = [s for s in stations if s.get("country") not in EXCLUDED_COUNTRIES]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    excluded = total - len(filtered)
    print(f"Fetched {total} stations.")
    print(f"Excluded {excluded} (Australia / New Zealand).")
    print(f"Wrote {len(filtered)} stations to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

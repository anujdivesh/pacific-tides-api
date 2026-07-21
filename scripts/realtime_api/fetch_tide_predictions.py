#!/usr/bin/env python3
"""Loop over stn_num values in stations.json, fetch tide predictions for each
from the sea-level API, and insert them into the tide_predictions table of
tidal.db. Duplicates are avoided by checking utc.
"""
import json
import os
import ssl
import sqlite3
import urllib.parse
import urllib.request

START_TIME = "2026-06-05T03:14:00"
END_TIME = "2027-07-07T02:55:00"
API_BASE = "https://sea-level-dev.cosppac.cloud//api/tide_predictions/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_JSON = os.path.join(BASE_DIR, "stations.json")
DB_PATH = os.path.join(BASE_DIR, os.pardir, os.pardir, "tidal.db")

# The endpoint's certificate chain doesn't validate locally.
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def fetch_predictions(stn_num):
    query = urllib.parse.urlencode(
        {"start_time": START_TIME, "end_time": END_TIME, "stn_num": stn_num}
    )
    url = f"{API_BASE}?{query}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    with open(STATIONS_JSON, "r", encoding="utf-8") as f:
        stations = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Track already-present (station_no, utc) pairs to skip duplicates.
        cur.execute("SELECT station_no, utc FROM tide_predictions")
        seen = {(row[0], row[1]) for row in cur.fetchall()}

        total_inserted = 0
        for station in stations:
            stn_num = station.get("stn_num")
            if not stn_num:
                continue

            try:
                records = fetch_predictions(stn_num)
            except Exception as exc:  # noqa: BLE001
                print(f"stn_num {stn_num}: fetch failed ({exc})")
                continue

            rows = []
            for rec in records:
                utc = rec.get("utc")
                if utc is None:
                    continue
                key = (stn_num, utc)
                if key in seen:
                    continue
                seen.add(key)
                rows.append((stn_num, utc, rec.get("height")))

            if rows:
                cur.executemany(
                    "INSERT INTO tide_predictions (station_no, utc, height) "
                    "VALUES (?, ?, ?)",
                    rows,
                )
                conn.commit()
                total_inserted += len(rows)

            print(
                f"stn_num {stn_num}: fetched {len(records)}, "
                f"inserted {len(rows)} new"
            )

        print(f"\nDone. Total new rows inserted: {total_inserted}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

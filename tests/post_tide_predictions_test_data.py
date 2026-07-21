"""Generate random tide_predictions (1-minute interval) spread across several
days of the current month, and POST them to the API.

Spreading the data over multiple calendar dates lets you test the delete
operation, e.g.:
    DELETE /tide/predictions/<station_no>?end_date=YYYY-MM-15&direction=before

Reads SECRET_TOKEN from the project's .env file and posts each generated
record to POST /tide/predictions.

Note: 1-minute resolution is 1440 records/day. --minutes-per-day keeps each
day's volume manageable while still covering many distinct dates.

Usage:
    python tests/post_tide_predictions_test_data.py
    python tests/post_tide_predictions_test_data.py --num-days 6 --minutes-per-day 120
    python tests/post_tide_predictions_test_data.py --month 2026-07 --station-no 200859
"""
import argparse
import calendar
import math
import os
import random
from datetime import datetime, timedelta

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

# Load .env from the project root (parent of the tests/ directory).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if load_dotenv:
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

STATION_NO = "200859"


def pick_days(year, month, num_days):
    """Return `num_days` day-numbers spread evenly across the month."""
    days_in_month = calendar.monthrange(year, month)[1]
    num_days = max(1, min(num_days, days_in_month))
    if num_days == 1:
        return [1]
    step = (days_in_month - 1) / (num_days - 1)
    return sorted({int(round(1 + i * step)) for i in range(num_days)})


def generate_records(station_no, year, month, days, minutes_per_day):
    """One prediction per minute for each chosen day, with a tide-like height.

    Height follows a ~12.4h semi-diurnal sine curve plus small noise. Each
    (station_no, utc) is unique -> no duplicates.
    """
    records = []
    period_minutes = 12.42 * 60  # semi-diurnal tidal period
    for day in days:
        amplitude = random.uniform(0.4, 0.9)
        mean_level = random.uniform(0.8, 1.2)
        phase = random.uniform(0, 2 * math.pi)
        day_start = datetime(year, month, day)
        for i in range(minutes_per_day):
            ts = day_start + timedelta(minutes=i)
            height = mean_level + amplitude * math.sin(2 * math.pi * i / period_minutes + phase)
            height += random.uniform(-0.02, 0.02)  # small noise
            records.append({
                "station_no": station_no,
                "utc": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                "height": round(height, 3),
            })
    return records


def main():
    parser = argparse.ArgumentParser(description="Post 1-min tide_predictions across a month.")
    parser.add_argument("--num-days", type=int, default=6,
                        help="How many distinct days to spread across the month (default 6).")
    parser.add_argument("--minutes-per-day", type=int, default=120,
                        help="1-min records per day (default 120 = 2 hours).")
    parser.add_argument("--month", default=None,
                        help="Month as YYYY-MM (default: current month).")
    parser.add_argument("--station-no", default=STATION_NO, help="station_no (default %s)." % STATION_NO)
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", "http://localhost:5000"),
                        help="API base URL (default http://localhost:5000).")
    args = parser.parse_args()

    token = os.getenv("SECRET_TOKEN")
    if not token:
        raise SystemExit("SECRET_TOKEN not found. Set it in .env or the environment.")

    if args.month:
        year, month = (int(x) for x in args.month.split("-"))
    else:
        now = datetime.now()
        year, month = now.year, now.month

    days = pick_days(year, month, args.num_days)
    date_labels = ["{:04d}-{:02d}-{:02d}".format(year, month, d) for d in days]

    url = args.base_url.rstrip("/") + "/tide/predictions"
    headers = {"Content-Type": "application/json", "X-Secret-Token": token}

    records = generate_records(args.station_no, year, month, days, args.minutes_per_day)
    created = duplicate = failed = 0

    print("Posting {} records for station_no {} to {}".format(len(records), args.station_no, url))
    print("Dates ({} min each): {}".format(args.minutes_per_day, ", ".join(date_labels)))
    for rec in records:
        resp = requests.post(url, json=rec, headers=headers)
        if resp.status_code == 201:
            created += 1
        elif resp.status_code == 409:
            duplicate += 1
        else:
            failed += 1
            print("  FAIL {} -> {} {}".format(rec["utc"], resp.status_code, resp.text.strip()))

    print("\nDone. created={} duplicate={} failed={}".format(created, duplicate, failed))
    print("\nTest delete, e.g.:")
    mid = date_labels[len(date_labels) // 2]
    print('  curl -X DELETE "{}/{}?end_date={}&direction=before" \\'.format(
        args.base_url.rstrip("/") + "/tide/predictions", args.station_no, mid))
    print('       -H "X-Secret-Token: $SECRET_TOKEN"')


if __name__ == "__main__":
    main()

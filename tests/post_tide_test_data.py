"""Generate random tide data for a station and POST it to the tide API.

Reads SECRET_TOKEN from the project's .env file and posts each generated
record to POST /tide/tides.

Usage:
    python tests/post_tide_test_data.py
    python tests/post_tide_test_data.py --days 5 --base-url http://localhost:5000
"""
import argparse
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

STATION_ID = "INT_TP0012"
MOON_PHASES = [
    "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
    "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
]


def generate_records(days, start_date):
    """Yield tide records: 2 highs + 2 lows per day, all with unique date_local.

    Uniqueness key on the API is (station_id, date_local, high_low), so we give
    every event a distinct timestamp.
    """
    records = []
    for day in range(days):
        base = start_date + timedelta(days=day)
        moon = random.choice(MOON_PHASES)
        # Sunrise in the morning (AM), sunset in the evening (PM).
        sunrise = base.replace(
            hour=random.randint(5, 6), minute=random.randint(0, 59)
        ).strftime("%I:%M %p")
        sunset = base.replace(
            hour=random.randint(17, 18), minute=random.randint(0, 59)
        ).strftime("%I:%M %p")

        # Four events through the day, alternating High/Low.
        for i, hour in enumerate([2, 8, 14, 20]):
            minute = random.randint(0, 59)
            event_time = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
            high_low = "High" if i % 2 == 0 else "Low"
            if high_low == "High":
                height = round(random.uniform(1.0, 1.8), 2)
            else:
                height = round(random.uniform(0.1, 0.6), 2)

            records.append({
                "station_id": STATION_ID,
                "high_low": high_low,
                "time": event_time.strftime("%H:%M"),
                "height": str(height),
                "date_local": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "moon": moon,
                "sunrise": sunrise,
                "sunset": sunset,
            })
    return records


def main():
    parser = argparse.ArgumentParser(description="Post random tide test data.")
    parser.add_argument("--days", type=int, default=7, help="Number of days to generate (default 7).")
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", "http://localhost:5000"),
                        help="API base URL (default http://localhost:5000).")
    parser.add_argument("--start", default=None,
                        help="Start date YYYY-MM-DD (default: today).")
    args = parser.parse_args()

    token = os.getenv("SECRET_TOKEN")
    if not token:
        raise SystemExit("SECRET_TOKEN not found. Set it in .env or the environment.")

    start_date = (
        datetime.strptime(args.start, "%Y-%m-%d") if args.start else datetime.now()
    ).replace(hour=0, minute=0, second=0, microsecond=0)

    url = args.base_url.rstrip("/") + "/tide/tides"
    headers = {"Content-Type": "application/json", "X-Secret-Token": token}

    records = generate_records(args.days, start_date)
    created = duplicate = failed = 0

    print("Posting {} records for {} to {}".format(len(records), STATION_ID, url))
    for rec in records:
        resp = requests.post(url, json=rec, headers=headers)
        if resp.status_code == 201:
            created += 1
        elif resp.status_code == 409:
            duplicate += 1
        else:
            failed += 1
            print("  FAIL {} {} -> {} {}".format(
                rec["date_local"], rec["high_low"], resp.status_code, resp.text.strip()))

    print("\nDone. created={} duplicate={} failed={}".format(created, duplicate, failed))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read scripts/stations.json and update `unit` and `flag` in the
country_mapper table of tidal.db, matching rows by station_id.
"""
import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_JSON = os.path.join(BASE_DIR, "stations.json")
DB_PATH = os.path.join(BASE_DIR, os.pardir, "tidal.db")


def main():
    with open(STATIONS_JSON, "r", encoding="utf-8") as f:
        stations = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        updated = 0
        missing = []
        for station in stations:
            station_id = station.get("station_id")
            unit = station.get("unit", "m")
            flag = station.get("flag", "")
            cur.execute(
                "UPDATE country_mapper SET unit = ?, flag = ? WHERE station_id = ?",
                (unit, flag, station_id),
            )
            if cur.rowcount:
                updated += cur.rowcount
                print(f"Updated {station_id}: unit='{unit}', flag='{flag}'")
            else:
                missing.append(station_id)

        conn.commit()
        print(f"\nDone. Rows updated: {updated}")
        if missing:
            print(f"No matching row for {len(missing)} station_id(s): {missing}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

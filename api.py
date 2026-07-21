import os
from db import get_db

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

# Columns that clients are allowed to set/update on country_mapper.
# `id` is auto-generated and never accepted from the client.
ALLOWED_COLUMNS = [
    "country_name",
    "country_code",
    "station_id",
    "station_name",
    "timezone",
    "lat",
    "lon",
    "status",
    "has_updates",
    "unit",
    "offset",
    "flag",
]


# Columns clients are allowed to set on the tide table.
# `id` is auto-generated and never accepted from the client.
TIDE_ALLOWED_COLUMNS = [
    "station_id",
    "high_low",
    "time",
    "height",
    "date_local",
    "moon",
    "sunrise",
    "sunset",
]

# Columns clients are allowed to set on the tide_predictions table.
# `id` is auto-generated and never accepted from the client.
PREDICTION_ALLOWED_COLUMNS = [
    "station_no",
    "utc",
    "height",
]


def verify_token(token):
    """Return True only when a token is configured and matches the request."""
    return bool(SECRET_TOKEN) and token == SECRET_TOKEN


def _station_exists(cursor, station_id):
    cursor.execute("SELECT 1 FROM country_mapper WHERE station_id = ?;", [station_id])
    return cursor.fetchone() is not None


def add_country_mapper(data):
    """Insert a new country_mapper row. Uniqueness is enforced on station_id."""
    fields = {k: data[k] for k in ALLOWED_COLUMNS if k in data}

    station_id = fields.get("station_id")
    if not station_id:
        return {"Error": "station_id is required"}, 400

    db = get_db()
    cursor = db.cursor()
    if _station_exists(cursor, station_id):
        return {"Error": "station_id already exists"}, 409

    columns = list(fields.keys())
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join('"{}"'.format(c) for c in columns)
    statement = "INSERT INTO country_mapper ({}) VALUES ({});".format(quoted, placeholders)
    cursor.execute(statement, [fields[c] for c in columns])
    db.commit()
    return {"message": "Created", "station_id": station_id}, 201


def update_country_mapper(station_id, data):
    """Update an existing country_mapper row identified by station_id."""
    # station_id is the key, not something you change here.
    fields = {k: data[k] for k in ALLOWED_COLUMNS if k in data and k != "station_id"}
    if not fields:
        return {"Error": "No valid fields provided"}, 400

    db = get_db()
    cursor = db.cursor()
    if not _station_exists(cursor, station_id):
        return {"Error": "Not found"}, 404

    assignments = ", ".join('"{}" = ?'.format(c) for c in fields)
    statement = "UPDATE country_mapper SET {} WHERE station_id = ?;".format(assignments)
    cursor.execute(statement, list(fields.values()) + [station_id])
    db.commit()
    return {"message": "Updated", "station_id": station_id}, 200


def delete_country_mapper(station_id):
    """Soft-delete a country_mapper row identified by station_id.

    Does not remove the row; instead flags it as inactive by setting
    has_updates = 1 (true) and status = 'N'.
    """
    db = get_db()
    cursor = db.cursor()
    if not _station_exists(cursor, station_id):
        return {"Error": "Not found"}, 404

    cursor.execute(
        "UPDATE country_mapper SET has_updates = 1, status = 'N' WHERE station_id = ?;",
        [station_id],
    )
    db.commit()
    return {"message": "Deleted", "station_id": station_id}, 200


def add_tide(data):
    """Insert a tide record.

    Uniqueness is enforced on the combination of (station_id, date_local, high_low)
    so the same tide event can't be recorded twice.
    """
    fields = {k: data[k] for k in TIDE_ALLOWED_COLUMNS if k in data}

    station_id = fields.get("station_id")
    date_local = fields.get("date_local")
    high_low = fields.get("high_low")
    if not station_id or not date_local or not high_low:
        return {"Error": "station_id, date_local and high_low are required"}, 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM tide WHERE station_id = ? AND date_local = ? AND high_low = ?;",
        [station_id, date_local, high_low],
    )
    if cursor.fetchone() is not None:
        return {"Error": "Duplicate record for station_id, date_local and high_low"}, 409

    columns = list(fields.keys())
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join('"{}"'.format(c) for c in columns)
    statement = "INSERT INTO tide ({}) VALUES ({});".format(quoted, placeholders)
    cursor.execute(statement, [fields[c] for c in columns])
    db.commit()
    return {"message": "Created", "id": cursor.lastrowid}, 201


# Direction of the delete relative to end_date -> SQL comparison operator.
#   "before" (default): remove rows dated earlier than end_date  (date_local < end_date)
#   "after":            remove rows dated later   than end_date  (date_local > end_date)
DELETE_DIRECTIONS = {"before": "<", "after": ">"}


def delete_tide(station_id, end_date, direction="before"):
    """Delete tide records for a station relative to end_date, then VACUUM.

    `direction` selects the comparison against end_date:
      - "before" -> date_local < end_date (delete everything below the date)
      - "after"  -> date_local > end_date (delete everything above the date)
    """
    if not end_date:
        return {"Error": "end_date is required"}, 400

    operator = DELETE_DIRECTIONS.get((direction or "before").lower())
    if operator is None:
        return {"Error": "direction must be 'before' or 'after'"}, 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM tide WHERE station_id = ? AND DATE(date_local) {} ?;".format(operator),
        [station_id, end_date],
    )
    deleted = cursor.rowcount
    db.commit()

    # VACUUM must run outside a transaction; commit above leaves us clear.
    cursor.execute("VACUUM;")

    return {"message": "Deleted", "station_id": station_id, "end_date": end_date,
            "direction": direction, "deleted": deleted}, 200


def add_tide_prediction(data):
    """Insert a tide_predictions record.

    Uniqueness is enforced on the combination of (station_no, utc) so the same
    prediction timestamp can't be recorded twice for a station.
    """
    fields = {k: data[k] for k in PREDICTION_ALLOWED_COLUMNS if k in data}

    station_no = fields.get("station_no")
    utc = fields.get("utc")
    if not station_no or not utc:
        return {"Error": "station_no and utc are required"}, 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM tide_predictions WHERE station_no = ? AND utc = ?;",
        [station_no, utc],
    )
    if cursor.fetchone() is not None:
        return {"Error": "Duplicate record for station_no and utc"}, 409

    columns = list(fields.keys())
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join('"{}"'.format(c) for c in columns)
    statement = "INSERT INTO tide_predictions ({}) VALUES ({});".format(quoted, placeholders)
    cursor.execute(statement, [fields[c] for c in columns])
    db.commit()
    return {"message": "Created", "id": cursor.lastrowid}, 201


def delete_tide_prediction(station_no, end_date, direction="before"):
    """Delete tide_predictions for a station relative to end_date, then VACUUM.

    `direction` selects the comparison against end_date (on the utc date):
      - "before" -> DATE(utc) < end_date (delete everything below the date)
      - "after"  -> DATE(utc) > end_date (delete everything above the date)
    """
    if not end_date:
        return {"Error": "end_date is required"}, 400

    operator = DELETE_DIRECTIONS.get((direction or "before").lower())
    if operator is None:
        return {"Error": "direction must be 'before' or 'after'"}, 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM tide_predictions WHERE station_no = ? AND DATE(utc) {} ?;".format(operator),
        [station_no, end_date],
    )
    deleted = cursor.rowcount
    db.commit()

    # VACUUM must run outside a transaction; commit above leaves us clear.
    cursor.execute("VACUUM;")

    return {"message": "Deleted", "station_no": station_no, "end_date": end_date,
            "direction": direction, "deleted": deleted}, 200

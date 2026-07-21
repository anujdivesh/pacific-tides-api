# Tide API

Endpoint to **add** a record to the `tide` table.

This is a write operation and requires a secret token. The token is read from the
`SECRET_TOKEN` environment variable (see `.env`) and must be sent in the
`X-Secret-Token` request header.

Base prefix: `/tide`

## Authentication

```
X-Secret-Token: <your-secret-token>
```

Missing or wrong token → `401 Unauthorized`:

```json
{ "Error": "Unauthorized" }
```

## Uniqueness

A record is considered a duplicate when another row already has the same
combination of **`station_id` + `date_local` + `high_low`**. Duplicates are
rejected with `409 Conflict` — the same tide event can't be stored twice.

## Fields

| Field        | Type     | Notes                              |
|--------------|----------|------------------------------------|
| `station_id` | string   | **required** (part of unique key)  |
| `date_local` | datetime | **required** (part of unique key)  |
| `high_low`   | string   | **required** (part of unique key)  |
| `time`       | string   |                                    |
| `height`     | string   |                                    |
| `moon`       | string   |                                    |
| `sunrise`    | string   |                                    |
| `sunset`     | string   |                                    |

`id` is auto-generated and cannot be set by the client. Unknown fields are ignored.

## Add a record

`POST /tide/tides`

```bash
curl -X POST http://localhost:5000/tide/tides \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: $SECRET_TOKEN" \
  -d '{
        "station_id": "INT_TP001",
        "high_low": "High",
        "time": "05:42",
        "height": "1.23",
        "date_local": "2026-07-21 05:42:00",
        "moon": "Waxing Gibbous",
        "sunrise": "06:15",
        "sunset": "18:02"
      }'
```

Response `201 Created`:

```json
{ "message": "Created", "id": 12345 }
```

## Delete records for a station

`DELETE /tide/tides/<station_id>?end_date=YYYY-MM-DD&direction=before`

Deletes records for the station relative to `end_date`, then runs `VACUUM` to
reclaim disk space.

Query parameters:

| Param       | Required | Values             | Meaning                                         |
|-------------|----------|--------------------|-------------------------------------------------|
| `end_date`  | yes      | `YYYY-MM-DD`       | The pivot date to compare against               |
| `direction` | no       | `before` (default) / `after` | `before` → delete `date_local < end_date`; `after` → delete `date_local > end_date` |

```bash
# delete everything BEFORE the date (default)
curl -X DELETE "http://localhost:5000/tide/tides/INT_TP0012?end_date=2026-07-27" \
  -H "X-Secret-Token: $SECRET_TOKEN"

# delete everything AFTER the date
curl -X DELETE "http://localhost:5000/tide/tides/INT_TP0012?end_date=2026-07-27&direction=after" \
  -H "X-Secret-Token: $SECRET_TOKEN"
```

Response `200 OK`:

```json
{ "message": "Deleted", "station_id": "INT_TP0012", "end_date": "2026-07-27", "direction": "before", "deleted": 28 }
```

`deleted` is the number of rows removed (`0` if nothing matched).

## Error responses

| Status | Body                                                                     | Meaning                                   |
|--------|--------------------------------------------------------------------------|-------------------------------------------|
| `400`  | `{ "Error": "station_id, date_local and high_low are required" }`        | A required field is missing (add)         |
| `400`  | `{ "Error": "end_date is required" }`                                    | Missing end_date on delete                |
| `400`  | `{ "Error": "direction must be 'before' or 'after'" }`                   | Invalid direction on delete               |
| `401`  | `{ "Error": "Unauthorized" }`                                            | Missing / invalid secret token            |
| `409`  | `{ "Error": "Duplicate record for station_id, date_local and high_low" }`| A matching record already exists          |

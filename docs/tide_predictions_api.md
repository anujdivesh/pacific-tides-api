# Tide Predictions API

Endpoints to **add** and **delete** records in the `tide_predictions` table.

These are write operations and require a secret token. The token is read from the
`SECRET_TOKEN` environment variable (see `.env`) and must be sent in the
`X-Secret-Token` request header.

Base prefix: `/tide`

> Note: reading predictions uses the existing `GET /tide/predictions?station_no=&start=&end=`.

## Authentication

```
X-Secret-Token: <your-secret-token>
```

Missing or wrong token → `401 Unauthorized`:

```json
{ "Error": "Unauthorized" }
```

## Uniqueness

A record is a duplicate when another row already has the same combination of
**`station_no` + `utc`**. Duplicates are rejected with `409 Conflict`.

## Fields

| Field        | Type   | Notes                             |
|--------------|--------|-----------------------------------|
| `station_no` | string | **required** (part of unique key) |
| `utc`        | string | **required** (part of unique key), ISO timestamp e.g. `2026-06-05T03:14:00` |
| `height`     | number |                                   |

`id` is auto-generated and cannot be set by the client. Unknown fields are ignored.

## Add a record

`POST /tide/predictions`

```bash
curl -X POST http://localhost:5000/tide/predictions \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: $SECRET_TOKEN" \
  -d '{
        "station_no": "200859",
        "utc": "2026-06-05T03:14:00",
        "height": 0.378
      }'
```

Response `201 Created`:

```json
{ "message": "Created", "id": 12345 }
```

## Delete records for a station

`DELETE /tide/predictions/<station_no>?end_date=YYYY-MM-DD&direction=before`

Deletes records for the station relative to `end_date` (compared on the `utc`
date), then runs `VACUUM` to reclaim disk space.

Query parameters:

| Param       | Required | Values             | Meaning                                         |
|-------------|----------|--------------------|-------------------------------------------------|
| `end_date`  | yes      | `YYYY-MM-DD`       | The pivot date to compare against               |
| `direction` | no       | `before` (default) / `after` | `before` → delete `DATE(utc) < end_date`; `after` → delete `DATE(utc) > end_date` |

```bash
# delete everything BEFORE the date (default)
curl -X DELETE "http://localhost:5000/tide/predictions/200859?end_date=2026-06-05" \
  -H "X-Secret-Token: $SECRET_TOKEN"

# delete everything AFTER the date
curl -X DELETE "http://localhost:5000/tide/predictions/200859?end_date=2026-06-05&direction=after" \
  -H "X-Secret-Token: $SECRET_TOKEN"
```

Response `200 OK`:

```json
{ "message": "Deleted", "station_no": "200859", "end_date": "2026-06-05", "direction": "before", "deleted": 1440 }
```

`deleted` is the number of rows removed (`0` if nothing matched).

## Error responses

| Status | Body                                                    | Meaning                          |
|--------|---------------------------------------------------------|----------------------------------|
| `400`  | `{ "Error": "station_no and utc are required" }`        | A required field is missing (add)|
| `400`  | `{ "Error": "end_date is required" }`                   | Missing end_date on delete       |
| `400`  | `{ "Error": "direction must be 'before' or 'after'" }`  | Invalid direction on delete      |
| `401`  | `{ "Error": "Unauthorized" }`                           | Missing / invalid secret token   |
| `409`  | `{ "Error": "Duplicate record for station_no and utc" }`| A matching record already exists |

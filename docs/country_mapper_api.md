# Country Mapper API

Endpoints to **add** and **update** rows in the `country_mapper` table.

Both endpoints are write operations and require a secret token. The token is
read from the `SECRET_TOKEN` environment variable (see `.env`) and must be sent
in the `X-Secret-Token` request header.

Base prefix: `/tide`

## Authentication

Send the token in the header:

```
X-Secret-Token: <your-secret-token>
```

Missing or wrong token → `401 Unauthorized`:

```json
{ "Error": "Unauthorized" }
```

## Fields

| Field          | Type    | Notes                          |
|----------------|---------|--------------------------------|
| `country_name` | string  |                                |
| `country_code` | string  | e.g. `FJ`                      |
| `station_id`   | string  | e.g. `INT_TP003`               |
| `station_name` | string  |                                |
| `timezone`     | string  | e.g. `+12`                     |
| `lat`          | number  |                                |
| `lon`          | number  |                                |
| `status`       | string  | e.g. `Y`                       |
| `has_updates`  | boolean |                                |
| `unit`         | string  | default `m`                    |
| `offset`       | string  | default `0`                    |
| `flag`         | string  | e.g. `FJ.png`                  |

Rows are keyed by **`station_id`** (must be unique). `id` is auto-generated and
cannot be set by the client. Any unknown fields are ignored.

## Add a row

`POST /tide/country_mapper`

`station_id` is required and must not already exist.

```bash
curl -X POST http://localhost:5000/tide/country_mapper \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: $SECRET_TOKEN" \
  -d '{
        "country_name": "Cook Islands",
        "country_code": "CK",
        "station_id": "INT_TP001",
        "station_name": "Rarotonga",
        "timezone": "-10",
        "lat": -21.20475,
        "lon": -159.784777777778,
        "status": "Y",
        "has_updates": true,
        "unit": "m",
        "offset": "0",
        "flag": "CK.png"
      }'
```

Response `201 Created`:

```json
{ "message": "Created", "station_id": "INT_TP001" }
```

Duplicate `station_id` → `409 Conflict`:

```json
{ "Error": "station_id already exists" }
```

## Update a row

`PUT /tide/country_mapper/<station_id>`

Only the fields you include are changed. `station_id` itself is the key and cannot
be changed via this endpoint.

```bash
curl -X PUT http://localhost:5000/tide/country_mapper/INT_TP001 \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: $SECRET_TOKEN" \
  -d '{
        "country_name": "Cook Islands",
        "country_code": "CK",
        "station_name": "Rarotonga",
        "timezone": "-10",
        "lat": -21.20475,
        "lon": -159.784777777778,
        "status": "Y",
        "has_updates": true,
        "unit": "m",
        "offset": "0",
        "flag": "CK.png"
      }'
```

Response `200 OK`:

```json
{ "message": "Updated", "station_id": "INT_TP001" }
```

Unknown station_id → `404 Not Found`:

```json
{ "Error": "Not found" }
```

## Error responses

| Status | Body                                        | Meaning                          |
|--------|---------------------------------------------|----------------------------------|
| `400`  | `{ "Error": "station_id is required" }`     | Missing station_id on add        |
| `400`  | `{ "Error": "No valid fields provided" }`   | No recognised fields on update   |
| `401`  | `{ "Error": "Unauthorized" }`               | Missing / invalid secret token   |
| `404`  | `{ "Error": "Not found" }`                  | station_id does not exist        |
| `409`  | `{ "Error": "station_id already exists" }`  | Duplicate station_id on add      |

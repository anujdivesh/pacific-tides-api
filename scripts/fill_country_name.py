import json
from collections import Counter
from typing import Any, Dict, List, Optional


PATH = "tide_gauge.json"


def extract_country(display_name: str) -> str:
    dn = (display_name or "").strip()
    if not dn:
        return ""

    # Most common: "Country, Place - ..."
    if "," in dn:
        return dn.split(",", 1)[0].strip()

    # Alternative: "Country - ..."
    if " - " in dn:
        return dn.split(" - ", 1)[0].strip()

    # Fallback
    if "-" in dn:
        return dn.split("-", 1)[0].strip()

    return dn


def norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


# Country/territory name -> flag asset key (from the user-provided MAP)
COUNTRY_TO_FLAG: Dict[str, str] = {
    "american samoa": "AS",
    "cook is": "CK",
    "cook islands": "CK",
    "fiji": "FJ",
    "micronesia": "FM",
    "federated states of micronesia": "FM",
    "mirconesia": "FM",  # typo seen in the source file
    "kiribati": "KI",
    "marshall is": "MH",
    "marshall islands": "MH",
    "new caledonia": "NC",
    "nauru": "NR",
    "niue": "NU",
    "french polynesia": "PF",
    "pitcairn": "PN",
    "papua new guinea": "PNG",
    "png": "PNG",
    "palau": "PW",
    "solomon is": "SB",
    "solomon islands": "SB",
    "tokelau": "TK",
    "tonga": "TO",
    "tuvalu": "TV",
    "vanuatu": "VU",
    "wallis and futuna": "WF",
    "samoa": "WS",
    "christmas island": "CX",
    "guam": "GU",
    "norfolk is": "NF",
    "norfolk island": "NF",
    "australia": "AU",
    "austalia": "AU",  # typo seen in the source file
    "new zealand": "NZ",
    "hawaii": "HW",
    "u.s. hawaii": "HW",
    "us hawaii": "HW",
    "phoenix islands": "PI",
}


def map_country_to_flag(country_raw: str) -> Optional[str]:
    c = norm(country_raw)

    # Handle variants like "New Caledonia Noumea"
    if "new caledonia" in c:
        return "NC"

    return COUNTRY_TO_FLAG.get(c)


def rebuild_row_with_country_name(row: Dict[str, Any], flag_code: Optional[str]) -> Dict[str, Any]:
    # Insert `country_name` immediately after `display_name` for consistency.
    new_row: Dict[str, Any] = {}
    inserted = False

    for k, v in row.items():
        if k == "country_name":
            continue
        new_row[k] = v
        if k == "display_name":
            new_row["country_name"] = flag_code
            inserted = True

    if not inserted:
        new_row["country_name"] = flag_code

    return new_row


def main() -> None:
    with open(PATH, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    unmapped = Counter()

    updated: List[Dict[str, Any]] = []
    for row in data:
        display_name = row.get("display_name", "")
        country_raw = extract_country(display_name)
        flag_code = map_country_to_flag(country_raw)

        if flag_code is None:
            unmapped[country_raw] += 1

        updated.append(rebuild_row_with_country_name(row, flag_code))

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Updated rows: {len(updated)}")
    if unmapped:
        print("Unmapped countries (country_name set to null):")
        for name, count in sorted(unmapped.items(), key=lambda kv: (-kv[1], kv[0].lower())):
            print(f"  {count:2d}  {name!r}")


if __name__ == "__main__":
    main()

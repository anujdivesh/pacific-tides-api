#!/usr/bin/env bash
#
# Download tidal.db from Wasabi (public URL) into the project directory,
# replacing the local tidal.db in place.
#
# Usage:
#   ./pull_db_from_wasabi.sh
#
set -euo pipefail

URL="https://s3.ap-southeast-2.wasabisys.com/spc-zarr-file/tidal.db/tidal.db"

# Resolve the directory this script lives in, so it works from any cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$SCRIPT_DIR/tidal.db"
TMP="$DEST.download.$$"

cleanup() { rm -f "$TMP"; }
trap cleanup EXIT

echo "Downloading tidal.db from Wasabi..."
echo "  URL:  $URL"
echo "  Dest: $DEST"

# Download to a temp file first; only replace the real db if it succeeds.
if command -v curl >/dev/null 2>&1; then
    curl -fL --progress-bar -o "$TMP" "$URL"
elif command -v wget >/dev/null 2>&1; then
    wget -O "$TMP" "$URL"
else
    echo "Error: neither curl nor wget is installed." >&2
    exit 1
fi

# Sanity check: file exists and is non-empty.
if [ ! -s "$TMP" ]; then
    echo "Error: downloaded file is empty." >&2
    exit 1
fi

mv "$TMP" "$DEST"
trap - EXIT

SIZE="$(du -h "$DEST" | cut -f1)"
echo "Done. tidal.db updated ($SIZE)."

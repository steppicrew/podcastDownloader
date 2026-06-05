#!/usr/bin/env bash
# Download all episodes of the "Professor van Dusen" podcast.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 download.py \
    'https://www.ardsounds.de/sendung/professor-van-dusen/urn:ard:show:8103e24c954e0404/' \
    "$@"

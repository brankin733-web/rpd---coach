#!/usr/bin/env bash
set -euo pipefail
base64 --decode rpd-coach-build-source.b64 > /tmp/rpd-coach-source.zip
unzip -q -o /tmp/rpd-coach-source.zip -d .
python3 scripts/apply-frame-workflow-patch.py .
python3 scripts/apply-landscape-board-patch.py .
python3 scripts/apply-production-access-patch.py .
npm install --no-audit --no-fund

#!/bin/sh
# Rebuild the pages and replace index.html / readings.html with password-protected (StatiCrypt) versions.
set -e
cd "$(dirname "$0")/.."
python3 tools/build.py
tmp=$(mktemp -d)
npx -y staticrypt index.html readings.html -p cnw2027 --short -d "$tmp" \
  --template-title "Strategy & Policy — Winter 2026–27" \
  --template-instructions "Enter the password to view this page."
cp "$tmp"/index.html "$tmp"/readings.html .
rm -rf "$tmp"

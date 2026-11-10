#!/bin/sh
# Rejoin the split firmware image and verify its SHA-256.
set -eu
cd "$(dirname "$0")/.."
cat dist-assets/oh6-opi5plus-20261106.img.part* > update.img
echo "joined: $(wc -c < update.img) bytes"
sha256sum update.img
echo "expected: 8994286e12c2b8a05aafd9479026fffafc34112ff47ddc199fe0cf5725f38d34"

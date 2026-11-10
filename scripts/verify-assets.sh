#!/bin/sh
# Verify every release asset against checksums/SHA256SUMS.txt.
set -eu
cd "$(dirname "$0")/.."
sha256sum -c checksums/SHA256SUMS.txt

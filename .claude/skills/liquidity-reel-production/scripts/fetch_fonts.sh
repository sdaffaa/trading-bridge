#!/usr/bin/env bash
# Download Tajawal (all weights) next to the build scripts — required before any build.
set -e
mkdir -p "$(dirname "$0")/fonts"
cd "$(dirname "$0")/fonts"
for f in Tajawal-Regular Tajawal-Medium Tajawal-Bold Tajawal-ExtraBold Tajawal-Black; do
  [ -f "$f.ttf" ] || curl -sL "https://raw.githubusercontent.com/google/fonts/main/ofl/tajawal/${f}.ttf" -o "${f}.ttf"
done
echo "fonts ready: $(ls *.ttf | wc -l)"

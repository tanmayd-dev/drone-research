#!/usr/bin/env bash
#
# Fails if any dashboard in visualizations/ is missing from the index, or if the
# index links to a dashboard that does not exist.
#
# Usage: scripts/check-index.sh   (works from any directory)

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(dirname -- "$script_dir")"

vis_dir="$root_dir/visualizations"
index_file="$vis_dir/index.html"

if [[ ! -f "$index_file" ]]; then
  echo "FAIL: index not found: $index_file" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf -- "$tmp_dir"' EXIT

# Dashboards on disk (sorted), excluding the index itself.
find "$vis_dir" -maxdepth 1 -type f -name '*.html' ! -name 'index.html' \
  -printf '%f\n' | LC_ALL=C sort > "$tmp_dir/on_disk"

# Links declared in the index. Only same-directory .html targets count.
grep -oE 'href="[^"]+\.html"' "$index_file" \
  | sed -E 's/^href="//; s/"$//; s/#.*$//' \
  | grep -vE '^([a-z][a-z0-9+.-]*:|/|\.\.?/)' \
  | LC_ALL=C sort -u > "$tmp_dir/linked" || true

comm -23 "$tmp_dir/on_disk" "$tmp_dir/linked" > "$tmp_dir/missing"
comm -13 "$tmp_dir/on_disk" "$tmp_dir/linked" > "$tmp_dir/broken"

total="$(wc -l < "$tmp_dir/on_disk" | tr -d ' ')"
linked_total="$(comm -12 "$tmp_dir/on_disk" "$tmp_dir/linked" | wc -l | tr -d ' ')"

echo "check-index: $index_file"
echo "check-index: dashboards on disk: $total"

status=0

if [[ -s "$tmp_dir/missing" ]]; then
  echo "FAIL: dashboards not linked from index.html:" >&2
  sed 's/^/  - visualizations\//' "$tmp_dir/missing" >&2
  status=1
fi

if [[ -s "$tmp_dir/broken" ]]; then
  echo "FAIL: index.html links to missing dashboards:" >&2
  sed 's/^/  - visualizations\//' "$tmp_dir/broken" >&2
  status=1
fi

if [[ "$status" -ne 0 ]]; then
  exit "$status"
fi

echo "check-index: linked dashboards: $linked_total/$total"
while IFS= read -r name; do
  echo "  OK  visualizations/$name"
done < "$tmp_dir/on_disk"
echo "check-index: PASS — every dashboard is indexed."

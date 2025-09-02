#!/bin/bash
set -e

# Extract files that need __future__ import annotations from ruff FA100 violations
echo "Files that need __future__ import annotations:"
files_to_update=$(uv run ruff check --select FA100 --output-format=json 2>/dev/null | \
    jq -r '.[].filename' | sort -u)

if [ -z "$files_to_update" ]; then
    echo "No files need __future__ import annotations!"
    exit 0
fi

echo "$files_to_update"

echo -e "\nProceed with adding __future__ import annotations to these files? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Add __future__ import to each file
echo "Adding __future__ import annotations..."
echo "$files_to_update" | while read -r file; do
    echo "  Processing: $file"
    sed -i '' '1i\
from __future__ import annotations' "$file"
done

echo "✅ __future__ import annotations added!"
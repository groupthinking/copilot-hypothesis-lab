#!/usr/bin/env bash
set -euo pipefail

# Check arguments
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <input_svg_path> [output_png_path]"
  exit 1
fi

INPUT_SVG="$1"
OUTPUT_PNG="${2:-${INPUT_SVG%.svg}.png}"

if [ ! -f "$INPUT_SVG" ]; then
  echo "Error: Input SVG file '$INPUT_SVG' does not exist."
  exit 1
fi

echo "Converting '$INPUT_SVG' to '$OUTPUT_PNG'..."
npx --yes resvg-cli "$INPUT_SVG" "$OUTPUT_PNG"
echo "Successfully converted '$INPUT_SVG' to '$OUTPUT_PNG'."

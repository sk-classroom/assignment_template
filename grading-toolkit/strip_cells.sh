#!/bin/bash
if [ "$#" -ne 2 ]; then
  echo "Usage: strip_cells.sh <input_file> <output_file>"
  echo "This script extracts the cells with tag = 'gradable' in a Jupyter notebook."
  exit 1
fi
jq '.cells |= map(select(.metadata.tags and (.metadata.tags | index("grading"))))' $1 > $2
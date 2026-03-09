#!/bin/sh
DIR="/disk3/wsl_tmp/Workspace210/test_data/"
OUTPUT_DIR_BASE="./tracking_results/"
CURRENT_DIR="$(pwd)"

python ./run_test.py --output_dir "$OUTPUT_DIR_BASE" --dir "$DIR" --modality "RGB"
python ./run_test.py --output_dir "$OUTPUT_DIR_BASE" --dir "$DIR" --modality "TIR"
OUTPUT_DIR_RGB="${OUTPUT_DIR_BASE}/RGB"
OUTPUT_DIR_TIR="${OUTPUT_DIR_BASE}/TIR"
OUTPUT_DIR_FINAL="${OUTPUT_DIR_BASE}" 

python ./linear.py --folder "$OUTPUT_DIR_RGB" --folder2 "$OUTPUT_DIR_TIR" --outputdir "$OUTPUT_DIR_FINAL"

# remove temporary per-modality output directories to save space
if [ -d "$OUTPUT_DIR_RGB" ]; then
  rm -rf "$OUTPUT_DIR_RGB"
fi
if [ -d "$OUTPUT_DIR_TIR" ]; then
  rm -rf "$OUTPUT_DIR_TIR"
fi

(
  cd "$OUTPUT_DIR_FINAL" || exit 1
  zip -j "$CURRENT_DIR/tracking_results.zip" ./*.txt
)


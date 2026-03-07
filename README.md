<div align="center">

# MADCTrack: Modality-Aware Divide-and-Conquer Track <br> for Modality-Missing RGBT Tracking

**Shilei Wang, Yipin Du, Yongkang Cheng, Pujian Lai, Dong Gao, and Gong Cheng**  

School of Automation, Northwestern Polytechnical University

</div>

---

## Overview

This repository contains the implementation of **MADCTrack**, a modality-aware divide-and-conquer framework for **modality-missing RGBT tracking**.

MADCTrack is implemented based on the DAM4SAM framework. Therefore, the environment setup, model configuration files, and pre-trained checkpoints remain the same as those used in the original DAM4SAM repository. Our main modification is in the **test-time pipeline**. Specifically, we perform tracking separately on the RGB and TIR modalities, then merge the two outputs to obtain the final tracking results.

The overall pipeline is simple and practical:

- use the same backbone and checkpoints as DAM4SAM,
- run testing on RGB frames,
- run testing on TIR frames,
- combine the two outputs with our merging script,
- save the final tracking results for submission.

---

## Installation

To set up the repository locally, follow these steps:

1. Clone the repository and navigate to the project directory:
    ```bash
    git clone https://github.com/wsumel/MADCTrack.git
    cd MADCTrack
    ```
2. Create a new conda environment and activate it:
   ```bash
    conda create -n madctrack_env python=3.10.15
    conda activate madctrack_env
    ```
3. Install torch and other dependencies:
   ```bash
   pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   ```

If you experience problems as mentioned here, including `ImportError: cannot import name '_C' from 'sam2'`, run the following command in the repository root:
    ```
    python setup.py build_ext --inplace
    ```
Note that you can still use the repository even with the warning above, but some postprocessing SAM2 steps may be skipped. For more information, consult the official [SAM2 installation instructions](https://github.com/facebookresearch/sam2).

## Getting started

Model checkpoints can be downloaded by running:
```bash
cd checkpoints && \
./download_ckpts.sh 
```

Our model configs are available in `sam2/` folder. 

## Testing

For evaluation, we use the same backbone, configuration files, and checkpoints as DAM4SAM.
The main difference is that testing is performed through our custom script test.sh.

The testing pipeline consists of the following steps:

1. Run tracking on the RGB modality.
2. Run tracking on the TIR modality.
3. Merge the two prediction results.
4. Remove temporary modality-specific folders.
5. Package the final results into a ZIP file.

## Prepare `test.sh`

Before running the evaluation, please edit the `test.sh` script and modify the dataset path and output directory according to your local environment.

Specifically, you need to update the following variables:

- `DIR` – path to the test dataset
- `OUTPUT_DIR_BASE` – directory where tracking results will be saved

An example `test.sh` script is shown below:

```bash
#!/bin/sh
DIR="/path/to/test_dataset/"
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
```

## Run testing

After editing the dataset path in `test.sh`, run:

```bash
bash test.sh

## Acknowledgments

Our implementation is built on top of [DAM4SAM](https://github.com/jovanavidenovic/DAM4SAM) and [SAM2](https://github.com/facebookresearch/sam2). We thank the original authors for making their code and models publicly available.
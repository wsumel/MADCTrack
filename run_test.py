import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
import glob
import argparse
import shutil

import numpy as np
import cv2
from PIL import Image

from dam4sam_tracker import DAM4SAMTracker
from utils.visualization_utils import overlay_mask, overlay_rectangle
from utils.box_selector import BoxSelector
from utils.mask_utils import mask2box, save_boxes


def run_sequence(dir_path, file_extension, output_dir,init_box):
    predictions = []
    history = []  # 保存历史预测 bbox（每帧一个 [x, y, w, h]）

    # Load frames from a given directory
    frames_dir = sorted(glob.glob(os.path.join(dir_path, '*.%s' % file_extension)))

    if len(frames_dir) == 0:
        print('Error: There is no frames in the given directory.')
        exit(-1)

    # # Select bounding box using click&hold box drawer
    # img0 = cv2.imread(frames_dir[0])
    # box_selector = BoxSelector()
    # init_box = box_selector.select_box(img0)

    # if not init_box:
    #     print('Error: Initialization box is not given')
    #     exit(-1)

    if type(init_box) == str:
        init_box = init_box.split(',')
        init_box = [int(init_box[0]),int(init_box[1]),int(init_box[2]),int(init_box[3])]
        print(init_box)
    else:
        init_box = [int(init_box[0]),int(init_box[1]),int(init_box[2]),int(init_box[3])]

    if not init_box:
        print('Error: Initialization box is not given')
        exit(-1)

    # Create tracker instance
    tracker = DAM4SAMTracker('sam21pp-L')

    # Handle saving output masks to the given output directory
    # Visualize tracking results if output directory is not given

    # Track frame-by-frame
    print('Segmenting frames...')
    for i in range(len(frames_dir)):
        import time
        st = time.time()
        img = Image.open(frames_dir[i])
        img_vis = np.array(img)

        if i == 0:
            outputs = tracker.initialize(img, None, bbox=init_box)
        else:
            outputs = tracker.track(img)
        ed = time.time()
        print("running time: ", ed-st)
        pred_mask = outputs['pred_mask']
        


        pred_bbox = mask2box(pred_mask)

        if pred_bbox is None:
            final_bbox = [-1,-1,-1,-1]
        else:
            final_bbox = pred_bbox

        history.append(final_bbox)

        predictions.append(final_bbox)
        
        
        
    print('Segmentation: Done.')
    return predictions

def main():
    parser = argparse.ArgumentParser(description='Run on a sequence of frames.')
    parser.add_argument('--dir', type=str, default='/disk3/wsl_tmp/Workspace210/public_data/', help='Path to directory with frames.')
    parser.add_argument('--ext', type=str, default='jpg', help='Image file extension.')
    parser.add_argument('--output_dir', type=str, default='/disk3/wsl_tmp/Workspace210/result_sam2_ir', help='Path to the output directory.')
    parser.add_argument('--modality', type=str, default='RGB', help='Modality of the input images.')
    
    args = parser.parse_args()

    # run_sequence(args.dir, args.ext, args.output_dir)
    args.output_dir = os.path.join(args.output_dir, args.modality)

    sub_dir  = os.listdir(args.dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    resultfiles = os.listdir(args.output_dir)

    for i in range(len(sub_dir)):
        print(sub_dir[i])
        if sub_dir[i]+'.txt' in resultfiles:
            continue
        sub_dir_path = os.path.join(args.dir,sub_dir[i])
        sequence_path = os.path.join(args.dir,sub_dir[i],args.modality)
        init_box = np.loadtxt(os.path.join(sub_dir_path,'init.txt'),dtype=int, delimiter=' ')
        print(init_box)
        results = run_sequence(sequence_path, args.ext, args.output_dir,init_box)
        print(results)
        save_dir = os.path.join(args.output_dir,sub_dir[i]+'.txt')
        print(save_dir)
        np.savetxt(save_dir,np.array(results),fmt='%f',delimiter=' ')







if __name__ == "__main__":
    main()
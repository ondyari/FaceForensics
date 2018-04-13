#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""
Script to extract images from the FaceForensics dataset

Usage:
    # Full cropped dataset
    python extract_images.py
        -i <input path with test/train/val folders>
        -o <output_path>
        --every_nth 1
    # 10 random cropped images of all videos
    python extract_images.py
        -i <input path with test/train/val folders>
        -o <output_path>
        --absolute_num 10
    # Extract from single folder
    python extract_images.py
        -i <input path, i.e. test/val or train folder>
        -o <output_path>
        --absolute_num 10
        -m single_folder
    # Extract from compressed videos but with uncompressed masks
    python extract_images.py
        -i <input path with test/train/val folders>
        -o <output_path>
        --absolute_num 10
        --mask_data_path <input path with test/train/val folders>
    # Full uncropped images + face masks
    python extract_images.py
        -i <input path with test/train/val folders>
        -o <output_path>
        --crop 0
        --every_nth 1
        --return_masks 1
"""
import cv2              # pip install opencv-python
import os
from os.path import join
import argparse
import random
import progressbar      # pip install progressbar2
import numpy as np


def get_non_zero_bb(img):
    # Get non zero elements for mask to get mask area
    a = np.where(img != 255)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox


def create_images_from_single_folder(data_path, output_path,
                                     absolute_num,
                                     every_nth,
                                     crop=1,
                                     scale=1.3,
                                     return_masks=0,
                                     mask_data_path=None,
                                     **kwargs):
    """
    Extract images from the FaceForensics dataset. Provide either 'absolute_num'
    for an absolute number of images to extract or 'every_nth' if you want to
    extract every nth image of a video.
    If you are only interested in face regions you can crop face regions with
    'crop_faces'. You can specify a 'scale' in order to get a bigger or smaller
    face region.

    :param data_path: contains 'altered', 'original' and maybe 'mask' folder
    :param output_path:
    :param absolute_num: if you want to extract an absolute number of images
    :param every_nth: if you want to extract a percentage of all images
    :param crop: if we crop images to face regions * scale or return full
    images (e.g. for localization)
    :param scale: extension of extracted face region in order to have the full
    face and a little bit of background
    :param mask_data_path: if 'mask' folder is not in data_path
    :param return_masks: if we should also create a folder containing all mask
    images in output_path
    :return:
    """
    # Input folders
    original_data_path = join(data_path, 'original')
    altered_data_path = join(data_path, 'altered')
    original_filenames = sorted(os.listdir(original_data_path))
    altered_filenames = sorted(os.listdir(altered_data_path))
    if crop or return_masks:
        if not mask_data_path:
            mask_data_path = join(data_path, 'mask')
        mask_filenames = sorted(os.listdir(mask_data_path))
    # Check if we have all files
    assert ([filename[:14] for filename in altered_filenames] ==
            [filename[:14] for filename in original_filenames]), \
           ("Incorrect number of files in altered and original. " +
            "Please check your folders and/or redownload.")
    if crop or return_masks:
        assert ([filename[:14] for filename in altered_filenames] ==
                [filename[:14] for filename in original_filenames]), \
            ("Incorrect number of files in original/altered and masks." +
             "Please check your folders and/or redownload.")

    # Create output folders
    original_images_output_path = join(output_path, 'original')
    altered_images_output_path = join(output_path, 'altered')
    mask_images_output_path = join(output_path, 'mask')
    os.makedirs(original_images_output_path, exist_ok=True)
    os.makedirs(altered_images_output_path, exist_ok=True)
    if return_masks:
        os.makedirs(mask_images_output_path, exist_ok=True)

    # Progressbar
    bar = progressbar.ProgressBar(max_value=len(altered_filenames))
    bar.start()
    for i in range(len(altered_filenames)):
        # Get readers
        altered_filename = altered_filenames[i]
        original_filename = original_filenames[i]
        altered_reader = cv2.VideoCapture(join(altered_data_path,
                                               altered_filename))
        original_reader = cv2.VideoCapture(join(original_data_path,
                                                original_filename))
        if crop or return_masks:
            mask_filename = mask_filenames[i]
            mask_reader = cv2.VideoCapture(join(mask_data_path, mask_filename))
        # Get number of frames
        number_of_frames = int(altered_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        if number_of_frames <= 0:
            print('Skipping ' + altered_filename +
                  ', invalid number of frames.')
            continue

        # Take video_num_images random frames
        image_frames = list(range(0, number_of_frames))
        assert bool(absolute_num) != bool(every_nth), \
            'You must specify either "absolute num" or "every_nth"'
        if absolute_num is not None and absolute_num > 0:
            absolute_num = min(absolute_num, number_of_frames)
            image_frames = random.sample(image_frames, absolute_num)
        elif absolute_num is not None and every_nth > 0:
            image_frames = image_frames[::every_nth]
        image_frames = sorted(image_frames)

        # Get dimension for scaling
        width = int(altered_reader.get(3))
        height = int(altered_reader.get(4))

        # Frame counter and output filename
        frame_number = 0
        image_counter = 0
        output_filename_prefix = altered_filename.split('.')[0] + '_'
        output_original_filename_prefix = original_filename.split('.')[0] + '_'
        if return_masks:
            mask_filename_prefix = mask_filename.split('.')[0] + '_'

        while altered_reader.isOpened():
            _, image = altered_reader.read()
            _, mask = mask_reader.read()
            _, original_image = original_reader.read()

            if image is None or mask is None or original_image is None:
                break

            if frame_number == image_frames[0]:
                if crop:
                    # Extract from mask bounding box. We convert mask to
                    # grayscale since we only care about non zero entries
                    gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                    y1, y2, x1, x2 = get_non_zero_bb(gray_mask)
                    size_bb = int(max(x2-x1, y2-y1) * scale)
                    center_x, center_y = (x1+x2)//2, (y1+y2)//2
                    # Check for out of bounds, x-y lower left corner
                    x1 = max(int(center_x - size_bb // 2), 0)
                    y1 = max(int(center_y - size_bb // 2), 0)
                    # Check for too big size for given x, y
                    size_bb = min(width - x1, size_bb)
                    size_bb = min(height - y1, size_bb)

                    # Crop frames
                    # Altered image
                    image = image[y1: y1+size_bb, x1: x1+size_bb]
                    # Original image
                    original_image = original_image[y1: y1 + size_bb,
                                                    x1: x1 + size_bb]
                    # Mask
                    if return_masks:
                        mask = mask[y1: y1 + size_bb, x1: x1 + size_bb]

                # Write to files
                # Altered
                output_altered_filename = output_filename_prefix + \
                                          str(image_counter) + '.png'
                cv2.imwrite(join(altered_images_output_path,
                                 output_altered_filename), image)
                # Original
                output_original_filename = output_original_filename_prefix + \
                                           str(image_counter) + '.png'
                cv2.imwrite(join(original_images_output_path,
                                 output_original_filename), original_image)
                # Mask
                if return_masks:
                    output_mask_filename = mask_filename_prefix + \
                                           str(image_counter) + '.png'
                    cv2.imwrite(join(mask_images_output_path,
                                     output_mask_filename), mask)

                image_counter += 1
                image_frames.pop(0)

                if len(image_frames) == 0:
                    break
            # Update frame number
            frame_number += 1

        # Release reader sand update progressbar
        altered_reader.release()
        original_reader.release()
        if crop or return_masks:
            mask_reader.release()
        bar.update(i)
    bar.finish()


def create_images_from_dataset(data_path, output_path, absolute_num, every_nth,
                               crop_faces=1,
                               scale=1.3,
                               return_masks=0,
                               mask_data_path=None,
                               **kwargs):
    for folder in os.listdir(data_path):
        if folder in ['test', 'val', 'train']:
            if not os.path.exists(join(data_path, folder)):
                print('Skipping {}'.format(join(data_path, folder)))
            else:
                print(join(data_path, folder))
            if mask_data_path:
                mask_data_path = join(mask_data_path, folder, 'mask')
            create_images_from_single_folder(data_path=join(data_path, folder),
                                             output_path=join(output_path,
                                                              folder),
                                             absolute_num=absolute_num,
                                             every_nth=every_nth,
                                             crop=crop_faces,
                                             scale=scale,
                                             return_masks=return_masks,
                                             mask_data_path=mask_data_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract images from the FaceForensics dataset.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--mode', '-m', default='whole_dataset',
                        help='Either "single_folder" for one folder '
                             '(train/test/val) or "whole_dataset" for all '
                             'folders to extract images from altered/original '
                             'and maybe mask videos.')
    parser.add_argument('--data_path', '-i',
                        help='Path to full FaceForensics dataset or single '
                             'folder (train/val/test)')
    parser.add_argument('--output_path', '-o',
                        help='Output folder for extracted images'
                        )
    parser.add_argument('--absolute_num', type=int, default=None,
                        help='Number of randomly chosen images/frames we create'
                             ' per video. Specify either absolute_num or nth '
                             'image')
    parser.add_argument('--every_nth', type=int, default=None,
                        help='Getting every nth image from all videos. Specify '
                             'either absolute_num or nth image')
    parser.add_argument('--mask_data_path', type=str, default=None,
                        help='If we extract from mask video files from a '
                             'different path (used e.g. for compression)')
    parser.add_argument('--return_masks', type=int, default=0,
                        help='If we also want to return mask images.')
    parser.add_argument('--scale', type=float, default=1.3,
                        help='Scale for cropped output images, i.e. if we '
                             'should take a bigger region around the face or '
                             'not.')
    parser.add_argument('--crop', type=int, default=1,
                        help='If we should crop out face regions or not.')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility '
                             '(or not if unspecified).')

    config, _ = parser.parse_known_args()

    # Random seed for reproducibility
    if config.seed is not None:
        random.seed(config.seed)

    kwargs = vars(config)

    if config.mode == 'single_folder':
        create_images_from_single_folder(**kwargs)
    elif config.mode == 'whole_dataset':
        create_images_from_dataset(**kwargs)
    else:
        print('Wrong mode, enter either "single_folder" or "whole_dataset".')

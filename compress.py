#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""
Script to compress videos in the FaceForensics dataset

Usage:
    python compress.py
        -i <input path with test/train/val folders>
        -o <output path>
        --crf <compression value>
"""
import os
from os.path import join
import argparse
from subprocess import Popen
import progressbar          # pip install progressbar2


def compress_with_ffmpeg_h264(data_path, output_path, crf=23,
                              **kwargs):
    """Compresses all files in a folder with ffmpeg, h264 codec and a specific
    crf."""
    files = os.listdir(data_path)
    bar = progressbar.ProgressBar(max_value=len(files))
    bar.start()
    os.makedirs(join(output_path), exist_ok=True)

    for i, file in enumerate(files):
        bar.update(i)
        Popen('ffmpeg -loglevel 0 -hide_banner -i ' + join(data_path, file)
              + ' -c:v libx264 -preset slow -crf ' + str(crf) +
              ' -c:a copy ' + join(output_path, file.split('.')[0]) + '.avi',
              shell=True).wait()
    bar.finish()


def compress_whole_folder_with_ffmpeg_h264(data_path, output_path, crf=0,
                                           **kwargs):
    """Generate compressed data with our folder structure"""
    for folder in os.listdir(data_path):
        if folder in ['test', 'train', 'val']:
            for subfolder in os.listdir(join(data_path, folder)):
                if subfolder in ['altered', 'original']:
                    print(folder, subfolder)
                    compress_with_ffmpeg_h264(data_path=join(data_path, folder,
                                                             subfolder),
                                              output_path=join(output_path,
                                                               folder,
                                                               subfolder),
                                              crf=crf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compress videos from the FaceForensics dataset.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--data_path', '-i')
    parser.add_argument('--output_path', '-o')
    parser.add_argument('--mode', '-m', default='whole_dataset',
                        help="Either 'single_folder' or 'whole_dataset'")
    parser.add_argument('--crf', type=int, default=0,
                        help='Compression coefficient, see '
                             'https://trac.ffmpeg.org/wiki/Encode/H.264. '
                             '0 = lossless compression, '
                             'up to ~23 = visually lossless'
                        )

    config = parser.parse_args()

    kwargs = vars(config)

    if config.mode == 'whole_dataset':
        compress_whole_folder_with_ffmpeg_h264(**kwargs)
    elif config.mode == 'single_folder':
        compress_with_ffmpeg_h264(**kwargs)
    else:
        print('Wrong mode, enter either "single_folder" or "whole_dataset".')

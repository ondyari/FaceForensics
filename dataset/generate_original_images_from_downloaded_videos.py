"""

Author: Andreas Rössler
"""
import os
from os.path import join
import argparse
from tqdm import tqdm
import shutil
import json
import cv2


def extract_sequences(data_path, **kwargs):
    images_out_path = join(data_path, 'original_sequences', 'raw', 'images')
    downloaded_videos_path = join(data_path, 'downloaded_videos')

    for video_id in tqdm(sorted(os.listdir(downloaded_videos_path))):
        sequences = []
        video_seq_path = join(downloaded_videos_path, video_id,
                              'extracted_sequences')
        # Our sequences are sorted
        for fn in sorted(os.listdir(video_seq_path)):
            with open(join(video_seq_path, fn), 'r') as seq_fn:
                seq = json.load(seq_fn)
            # Check if we already extracted it successfully
            num_images = len(seq)
            seq_images_out_path = join(images_out_path, video_id)
            if (os.path.isdir(images_out_path) and
                    video_id in os.listdir(images_out_path) and
                    len(os.listdir(seq_images_out_path)) == num_images):
                tqdm.write('Skipping {} {}'.format(video_id, fn))
            else:
                tqdm.write('Writing new video {} {}'.format(video_id, fn))
                # Save
                sequences.append(seq)
        # Skip already extracted videos
        if len(sequences) == 0:
            continue

        # Open reader
        reader = cv2.VideoCapture(join(downloaded_videos_path, video_id,
                                       video_id + '.mp4'))
        frame_num = 0
        curr_seq = 0
        curr_seq_image_count = 0

        while reader.isOpened():
            _, image = reader.read()
            if image is None:
                break

            if frame_num in sequences[curr_seq]:
                out_folder = str(video_id) + '_' + str(curr_seq)
                os.makedirs(join(images_out_path, out_folder),
                            exist_ok=True)
                out_fn = '{0:04d}.png'.format(curr_seq_image_count)
                cv2.imwrite(join(images_out_path, out_folder, out_fn),
                            image)
                curr_seq_image_count += 1

            if frame_num >= sequences[curr_seq][-1]:
                curr_seq += 1
                if curr_seq > len(sequences) - 1:
                    break

            frame_num += 1
        # Finish reader
        reader.release()


def create_conversion_list(data_path, **kwargs):
    output_path = join(data_path, 'misc', 'conversion_dict')
    data_path = join(data_path, 'original_sequences')

    filelist = sorted(os.listdir(join(data_path, 'raw', 'images')))
    conversion_dict = {}
    assert len(filelist) <= 1000, 'Filelist too long'

    for i, fn in enumerate(filelist):
        out_fn = '{:03d}'.format(i)
        # Youtube ids are 11 characters long
        conversion_dict[out_fn] = fn[:11] + ' ' + fn[12:]
        A = join(data_path, 'images', fn)
        B = join(data_path, 'images', out_fn)
        shutil.move(A, B)

    with open(output_path, 'w') as outfile:
        json.dump(conversion_dict, outfile, sort_keys=True,
                  indent=4, separators=(',', ': '))


def rename_from_conversion_list(data_path, **kwargs):
    data_path = join(data_path, 'original_sequences')
    list_path = join(data_path, 'misc', 'conversion_dict.json')
    with open(list_path, 'r') as f:
        conversion_list = json.load(f)
        conversion_list = {'_'.join(v.split(' ')): k for k, v in 
                           conversion_list.items()}

    for file in os.listdir(data_path):
        shutil.move(join(data_path, file),
                    join(data_path,conversion_list[file]))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data_path', '-i',
                   default='/mnt/canis/Datasets/FaceForensics/v3')
    p.add_argument('--mode', '-m',
                   default='extract')
    args = p.parse_args()
    vargs = vars(args)

    # download_from_csv(**vargs)
    if args.mode == 'extract':
        extract_sequences(**vargs)
    elif args.mode == 'conversion_list':
        create_conversion_list(**vargs)
    else:
        print('Wrong mode {}'.format(args.mode))

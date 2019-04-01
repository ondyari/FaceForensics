"""
Compresses the FaceForensics and FaceForensics++ raw image datasets.

See https://github.com/ondyari/FaceForensics or python compress.py -h for
instructions

Author: Andreas Rössler
"""
import os
import argparse
from tqdm import tqdm
from os.path import join
import json
import subprocess


def extract_frames(data_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    subprocess.check_output('ffmpeg -i {} -start_number 0 {}'.format(
        data_path, join(output_path, '%04d.png')),
        shell=True, stderr=subprocess.STDOUT)


def make_video_from_images(data_path, output_path,
                           crf=0, fps=30):
    # Video color space is different from RGB by default which we want to have
    # when converting loss-less
    codec = 'libx264' if crf != 0 else 'libx264rgb'
    subprocess.check_output(
        'ffmpeg -r {} -i {} -crf {} -c:v {} -vf "fps={}" {}'.format(
            str(fps), join(data_path, '%04d.png'), str(crf), codec, str(fps),
            output_path),
        shell=True, stderr=subprocess.STDOUT)


def create_fps_dict(data_path):
    with open(join(data_path, 'misc', 'conversion_list.json'), 'r') as f:
        conversion_dict = json.load(f)

    fps_dict = {}
    for key in conversion_dict.keys():
        video_id, num = conversion_dict[key].split(' ')
        with open(join(data_path, 'downloaded_videos', video_id,
                       video_id + '.json'), 'r') as f:
            info_dict = json.load(f)
        fps_dict[key] = info_dict['fps']
    return fps_dict


def compress_folder(data_path, output_path, crf, fps, **kwargs):
    for folder in tqdm(os.listdir(data_path)):
        make_video_from_images(
            join(data_path, folder),
            join(output_path, folder + '.mp4'),
            crf=crf, fps=fps,
        )


def compress_video_folder(data_path, output_path, crf, fps, **kwargs):
    codec = 'libx264' if crf != 0 else 'libx264rgb'
    os.makedirs(output_path, exist_ok=True)
    for video in tqdm(os.listdir(data_path)):
        subprocess.check_output(
            'ffmpeg -r {} -i {} -crf {} -c:v {} -vf "fps={}" {}'.format(
                str(fps), join(data_path, video), str(crf), codec,
                str(fps),
                join(output_path, video)),
            shell=True, stderr=subprocess.STDOUT)


def compress_v1(data_path, output_path, crf, fps, **kwargs):
    for dtype in ['source_to_target/raw', 'selfreenactment/raw']:
        print(dtype)
        for set_type in os.listdir(join(data_path, dtype)):
            for man_type in os.listdir(join(data_path, dtype, set_type)):
                path = join(dtype, set_type, man_type)
                print(man_type)
                os.makedirs(join(output_path, path), exist_ok=True)
                compress_video_folder(join(data_path, path),
                                      join(output_path, path),
                                      crf=crf, fps=fps)


def create_compressed_method(data_path, method='Face2Face',
                             extract_images=True,
                             **kwargs):
    # 1. Extract fps for all files
    fps_dict = create_fps_dict(data_path)

    # 2. Compress method folder
    if method == 'original':
        images_path = join(data_path, 'original_sequences', 'raw', 'images')
        compressed_path = join(data_path, 'original_sequences')
    else:
        images_path = join(data_path, 'manipulated_sequences', method, 'raw',
                           'images')
        compressed_path = join(data_path, 'manipulated_sequences', method)

    for crf in [0, 23, 40]:
        print('Starting ', crf)
        videos_output_path = join(compressed_path, 'c'+str(crf), 'videos')
        images_output_path = join(compressed_path, 'c'+str(crf), 'images')
        os.makedirs(videos_output_path, exist_ok=True)
        if extract_images:
            os.makedirs(images_output_path, exist_ok=True)

        for folder in tqdm(sorted(os.listdir(images_path))):
            out_fn = join(videos_output_path, folder + '.mp4')
            if method == 'original':
                fps = fps_dict[folder]
            else:
                # We take the fps of the source video for manipulated videos
                fps = fps_dict[folder.split('_')[-1]]
            # Compress as video
            if not os.path.exists(out_fn):
                make_video_from_images(
                    join(images_path, folder),
                    out_fn,
                    crf=crf, fps=fps,
                )

            if extract_images:
                # Check for correct extraction or repeat where we left of
                try:
                    num_out_frames = len(os.listdir(join(images_output_path,
                                                         folder)))
                    num_in_frames = len(os.listdir(join(images_path, folder)))
                    if not (os.path.exists(join(images_output_path, folder)) and
                            num_in_frames == num_out_frames):
                        # Extract images
                        extract_frames(out_fn, join(images_output_path, folder))
                except FileNotFoundError:
                    # Extract images
                    extract_frames(out_fn, join(images_output_path, folder))
                # Check if everything was correct
                num_out_frames = len(
                    os.listdir(join(images_output_path, folder)))
                num_in_frames = len(os.listdir(join(images_path, folder)))
                if num_in_frames != num_out_frames:
                    tqdm.write('Number of frames in {} is wrong: {}/{}'.format(
                        folder, num_out_frames, num_in_frames
                    ))


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument('--mode', '-m', default='compress_all')
    p.add_argument('--data_path', '-i', type=str)
    p.add_argument('--output_path', '-o', type=str)
    p.add_argument('--method', default='original')
    p.add_argument('--crf', type=int, default=0)
    p.add_argument('--fps', type=int, default=30)
    args = p.parse_args()

    if args.mode == 'compress_folder':
        compress_video_folder(**vars(args))
    elif args.mode == 'create_method':
        create_compressed_method(**vars(args))
    if args.mode == 'compress_v1-all':
        compress_v1(**vars(args))
    elif args.mode == 'compress_all':
        for method in ['Face2Face', 'FaceSwap', 'Deepfakes']:
            args.method = method
            print(args.method)
            create_compressed_method(**vars(args))

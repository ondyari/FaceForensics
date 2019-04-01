"""
DeepFakes generation file. For more information visit
https://github.com/ondyari/FaceForensics

Author: Andreas Roessler
"""
import os
from os.path import join
import argparse
from tqdm import tqdm
import subprocess
import random
import shutil
import time
import datetime
import json
from distutils.dir_util import copy_tree


deepfakes_path = os.path.abspath('faceswap-master/faceswap.py')


def train(data_path1, data_path2, model_path, python_path, gpu=0,
          iterations=200000):
    os.makedirs(model_path, exist_ok=True)
    subprocess.check_output(
        'CUDA_VISIBLE_DEVICES={} {} {} train -A {} -B {} -m {} -it {}'.format(
            gpu, python_path, deepfakes_path, data_path1, data_path2,
            model_path, iterations),
        shell=True, stderr=subprocess.STDOUT
    )


def convert_frames_to_data(data_path, output_path, python_path,
                           gpu=0, alignments_path=None):
    os.makedirs(output_path, exist_ok=True)
    if alignments_path is not None:
        align = '--alignments {}'.format(alignments_path)
    else:
        align = ''
    subprocess.check_output(
        'CUDA_VISIBLE_DEVICES={} {} {} extract -i {} -o{} {}'.format(
            gpu, python_path, deepfakes_path, data_path, output_path, align),
        shell=True, stderr=subprocess.STDOUT
    )


def convert(data_path, output_path, model_path, gpu, python_path,
            swap_models=False, alignments_path=None, write_image_masks=None):
    os.makedirs(output_path, exist_ok=True)
    swap = '--swap-model' if swap_models else ''
    if alignments_path is not None:
        align = '--alignments {}'.format(alignments_path)
    else:
        align = ''
    if write_image_masks:
        os.makedirs(write_image_masks, exist_ok=True)
        write_image_masks = '--write_image_masks {}'.format(write_image_masks)
    else:
        write_image_masks = ''
    subprocess.check_output(
        'CUDA_VISIBLE_DEVICES={} {} {} convert -i {} -o {} '
        '-m {} {} {} {} --seamless'
        .format(gpu, python_path, deepfakes_path,  data_path, output_path,
                model_path, swap, align, write_image_masks),
        shell=True, stderr=subprocess.STDOUT)


def generate_models(data_path, output_path, gpu, iterations, python_path,
                    filelist=None,
                    convert_images=True,
                    keep_temp_directories=True,
                    **kwargs
                    ):
    """
    Runs the full deepfakes script and creates output folders for all videos.
    We take pairs of two videos in the input path and train a model on these.

    :param data_path: contains image folders
    :param output_path: we create a single folder where we store all outputs of
    our script. This includes:
        - model files
        - manipulated images
    :param gpu: which gpu to use for training
    :param iterations: after how many iterations training has to stop
    :param python_path: absolute path to python
    :param filelist: contains pairs of input folders to manipulate. If "None" we
    take all input files and randomly
    :param convert_images: if we should convert the input images directly after
    training our models
    :param keep_temp_directories: if we should keep temporary directories
    produced by the respective sub-functions (a lot of files)
    :return:
    """
    if not filelist:
        assert len(os.listdir(data_path)) % 2 == 0,\
            'Odd number of folders in data_path, please provide a filelist ' +\
            'or delete a file'
        input_files = os.listdir(data_path)
        random.shuffle(input_files)
    else:
        # Open filelist and add them all to one list, ordered pairs
        with open(filelist, 'r') as f:
            filelist = json.load(f)
            input_files = []
            for pair in filelist:
                input_files.append(pair[0])
                input_files.append(pair[1])

    print('-'*80)
    print('Starting main')
    print('-'*80)
    for i in tqdm(range(0, len(input_files), 2)):
        start_time = time.time()

        # File names for input and output
        path1 = input_files[i]
        path2 = input_files[i+1]
        output_fn = str(path1) + '_' + str(path2)
        tqdm.write('Starting {}'.format(output_fn))
        # Output folder
        output_folder_path = join(output_path, output_fn)
        os.makedirs(output_folder_path, exist_ok=True)

        # 1. Copy images for safety
        for apath in [path1, path2]:
            tqdm.write('Copying {} images'.format(apath))
            copy_tree(join(data_path, apath), join(output_folder_path, apath))

        # 2. Prepare images for training
        for apath in [path1, path2]:
            tqdm.write('Prepare {} images for training'.format(apath))
            convert_frames_to_data(join(output_folder_path, apath),
                                   join(output_folder_path, apath + '_faces'),
                                   gpu=gpu, python_path=python_path,
                                   alignments_path=join(output_folder_path,
                                   '{}_alignment.txt'.format(apath)))

        # Time
        prep_finished_time = time.time()
        time_taken = time.time() - start_time
        tqdm.write('Finished preparation in {}'.format(
            str(datetime.timedelta(0, time_taken))))

        # 3. Train deepfakes model
        tqdm.write('Start training with {} iterations on gpu {}'.format(
            iterations, gpu))
        train(data_path1=join(output_folder_path, path1 + '_faces'),
              data_path2=join(output_folder_path, path2 + '_faces'),
              model_path=join(output_folder_path, 'models'),
              gpu=gpu, iterations=iterations, python_path=python_path)

        # Time
        time_taken = time.time() - prep_finished_time
        tqdm.write('Finished training in {}'.format(
            str(datetime.timedelta(0, time_taken))))

        # 4. Convert images with trained model
        folders_to_keep = ['models']
        if keep_temp_directories and convert_images:
            for apath in [path1, path2]:
                tqdm.write('Converting images: {}'.format(apath))
                out_path = path1 + '_' + path2 if apath == path1 else \
                    path2 + '_' + path1
                folders_to_keep.append(out_path)
                convert(data_path=join(data_path, path1),
                        output_path=join(output_folder_path, out_path),
                        model_path=join(output_folder_path, 'models'),
                        gpu=gpu,
                        python_path=python_path,
                        alignments_path=join(output_folder_path,
                                             '{}_alignment.txt'.format(apath)),
                        write_image_masks=join(output_folder_path,
                                               out_path + '_mask')
                        )

        # Cleaning up
        if not keep_temp_directories:
            tqdm.write('Cleaning up')
            for folder in os.listdir(output_folder_path):
                if folder not in folders_to_keep:
                    folder_path = join(output_folder_path, folder)
                    if os.path.isfile(folder_path):
                        os.remove(folder_path)
                    else:
                        shutil.rmtree(folder_path)

        # Time
        time_taken = time.time() - start_time
        tqdm.write('Finished in {}'.format(
            str(datetime.timedelta(0, time_taken))))


def create_from_models(models_path, images_path, output_path, python_path,
                       gpu=0, copy_models=True,
                       **kwargs):
    images_output_path = join(output_path, 'images')
    masks_output_path = join(output_path, 'masks')
    alignments_output_path = join(output_path, 'alignments')
    os.makedirs(alignments_output_path, exist_ok=True)
    mod_out_path = join(output_path, 'models')
    os.makedirs(mod_out_path, exist_ok=True)
    if copy_models:
        os.makedirs(join(output_path, 'models'), exist_ok=True)

    print('Starting process')

    count = 0
    files = sorted(os.listdir(models_path))
    video_files = sorted(os.listdir(images_path))

    for file in tqdm(files):
        file2 = "_".join(file.split('_')[::-1])
        if not (file.split('_')[0] in video_files and file2.split('_')[0] in
                video_files):
            continue
        tqdm.write('Starting {} and {}'.format(file, file2))

        if os.path.exists(join(images_output_path, file)) and \
           os.path.exists(join(images_output_path, file2)) and \
           os.path.exists(join(mod_out_path, file)):
            tqdm.write('Skipping {}'.format(file))
            count += 1
            continue

        # 1. Convert images
        for chosen_file in [file, file2]:
            tqdm.write('Converting {}'.format(chosen_file))
            swap_models = True if chosen_file == file2 else False
            model_path = join(models_path, file)
            if os.path.exists(join(model_path, 'models')):
                model_path = join(model_path, 'models')
            convert(data_path=join(images_path, chosen_file.split('_')[0]),
                    output_path=join(images_output_path, chosen_file),
                    model_path=model_path,
                    gpu=gpu,
                    swap_models=swap_models,
                    alignments_path=join(alignments_output_path,
                                         '{}.json'.format(chosen_file)),
                    write_image_masks=join(masks_output_path, chosen_file),
                    python_path=python_path)

        # 2. Copy models
        if copy_models:
            tqdm.write('Copy models')
            file_mod_out_path = join(mod_out_path, file)
            copy_tree(join(models_path, file, 'models'), file_mod_out_path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode', '-m', default='generate_models')
    p.add_argument('--data_path', '-i', type=str)
    p.add_argument('--data_path2', '-i2', type=str)
    p.add_argument('--output_path', '-o', type=str,
                   default='output')
    p.add_argument('--python_path', type=str)
    p.add_argument('--model_path', type=str)
    p.add_argument('--gpu', type=str, default='0')
    p.add_argument('--iterations', '-it', type=int, default=200000)
    p.add_argument('--keep_temp_directories', action='store_true')
    p.add_argument('--convert_images', action='store_true')
    args = p.parse_args()
    mode = args.mode

    # Convert images to input data
    if mode == 'extract_faces':
        convert_frames_to_data(data_path=args.data_path,
                               output_path=args.output_path,
                               alignments_path=join(args.output_path,
                                                    'alignments.json'),
                               python_path=args.python_path)
    # Train model on extracted data
    elif mode == 'train':
        train(data_path1=args.data_path, data_path2=args.data_path2,
              model_path=args.model_path, gpu=args.gpu,
              python_path=args.python_path)
    # Convert video/images with trained model
    elif mode == 'convert':
        convert(**vars(args))
    # Full script
    elif mode == 'generate_models':
        generate_models(**vars(args))
    elif mode == 'create_from_models':
        create_from_models(models_path=args.data_path,
                           images_path=args.data_path2,
                           **vars(args))

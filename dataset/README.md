# Dataset

![Header](../images/teaser.png)

If you would like to download the FaceForensics++ data, please fill out [this google form](https://docs.google.com/forms/d/e/1FAIpQLSdRRR3L5zAv6tQ_CKxmK4W96tAab_pfBu2EKAgQbeDVhmXagg/viewform) and, once accepted, we will send you the link to our download script.. You will get a link to the download script which will be used throughout this text to obtain the full dataset. This includes 977 downloaded videos from youtube, 1000 original extracted sequences that contain a unobstructed face that can be easily tracked, as well as their manipulated versions using our three methods: Deepfakes, Face2Face and FaceSwap. We also provide all Deepfakes models.

There are two ways to get the dataset: you can use the script to download all images or videos or generate most of the data on your own using the scripts provided in this folder which saves quite a bit of bandwidth if you are interested in the raw image material. However, you will have to download the Face2Face manipulated videos/images as there is no publicly available implementation to generate them from scratch. 

The dataset has the following folder structure which will either be produced by the download or generation scripts.

```shell
FaceForensics++ dataset
|-- downloaded_videos
    < contains all original downloaded videos, video information files and their extracted sequences
      which can be used to extract the original sequences used in the dataset >
|-- original_sequences
    < c0/raw original sequence images/videos >
    < c23/hq original sequence images/videos >
    < c40/lq original sequence images/videos >
|-- manipulated_sequenecs
    |-- Deepfakes
    < Deepfake sequence images/videos of all three compression degrees as well as models and masks after poisson image editing>
    |-- Face2Face
    < Face2Face sequence images/videos of all three compression degrees as well as masks >
    |-- FaceSwap
    < FaceSwap sequence images/videos of all three compression degrees as well as masks >
    |-- NeuralTextures
    < NeuralTextures sequence images/videos of all three compression degrees as well as masks >
```

We renamed all original sequences to integers between `0` and `999`. The original youtube id's can be recovered using `conversion_dict.json`.

Here is a overview of the space required to save/download the dataset:

- The original downladed videos from youtube: 38.5GB
- All h264 compressed videos with compression rate factor
    - 0: ~400GB
    - 23: ~8GB
    - 40: ~1GB
- All raw extracted images as pngs: ~2TB

## 1. Download script

### General usage
Please consult

`python download-FaceForensics_v3.py -h`

for a detailed overview of the download scrips parameter choices and their respective defaults. The general usage is as follows:

```shell
python download-FaceForensics_v3.py
    <output path>
    -d <dataset type, e.g., Face2Face, original or all>
    -c <compression quality, e.g., c23 or raw>
    -t <file type, e.g., videos, masks or models>
```

We advise you to download the compressed videos and extract the frames on your own as the raw file sizes are quite large. If you are interested in reproducing our steps, you might consider generating them by yourself as outlined below.

*Update:* We no longer offer the download of images as you can extract those from the lossless compressed c0 videos

### Examples
In order to download all light compressed (i.e., a visually lossless compression rate factor of 23 using the h264 codec) original as well as altered videos of all three manipulation methods use

`python download-Faceforensics_v3.py <output path> -d all -c c23 -t videos`

For all lossless compressed (i.e., a compression rate factor of 0) extracted original videos run

`python download-FaceForensics_v3.py <output path> -d original -c c0 -t videos`

With

`python download-FaceForensics_v3.py <output path> -d Face2Face -t masks`

you obtain the corresponding masks of the chosen method, i.e., a binary mask indicating the manipulated pixels.

### Original Videos

You can download the original videos that were downloaded from youtube using

`python download-FaceForensics_v3.py <output path> -d original_youtube_videos`

The zipped file contains all downloaded videos in their original length as well as a json file containing the frames that were extracted for our dataset.


### Audio

We only downloaded the source video without audio. However, you can re-download and extract the audio using the frame numbers that you obtain by downloading the original youtube videos. If you want to save bandwidth, you can only obtain the frame location and youtube ids using:

`python download-FaceForensics_v3.py <output path> -d original_youtube_videos_info`

### Masks

We provide binary masks for all our manipulation methods. For FaceSwap and Face2Face those masks are pretty self-explanatory. However, it is more difficult for DeepFakes and NeuralTextures.
- Deepfakes: after we feed in our face through the auto-encoder and warp it back to the image, we apply Poisson image editing. This process is done on a rectangular box around the face. Please consult the [DeepFakes readme](datasets/DeepFakes).
- NeuralTextures: NeuralTextures takes a 1.7 scaled part around the face bounding box of the Face2Face tracker as input and manipulates the whole region. However, the method has skip connections which allow it to directly copy pixel values from non-face areas of this crop. The NeuralTexture masks report the tracking results for those regions, though we will upload the manipulated regions as well and add more details to this process soon.


### Frame Extraction

You easily extract the images frames with either `ffmpeg` or `opencv`. You can use

`python extracted_compressed_videos.py <output path> -d <"all" or single dataset via "Face2Face" or "original"> -c c0`

The c0/raw videos are lossless compressed, meaning the extracted images (saved as a png) are 100% the same as our raw images used in the paper (tested using opencv for extraction).

## 2. Dataset generation

For DeepFakes and FaceSwap see the respective directories. As Face2Face is not publicly available, you have to download those videos yourself and extract the frames. 

## 3. File splits

Our used dataset file splits can be found in the [respective folder](splits). We used 720 videos for train and 140 videos for validation as well as testing.

## 4. Compression

### Setup

Run `bash setup_ffmpeg_h264.sh` to install ffmpeg together with the h264 codec.

### Paper Compression

Once, you have downloaded/extracted all raw images, you can use

`python compress.py
    -i <path to FaceForensics++ folder including original and manipulated sequences folders>`

to compress the data in the same manner as described in the paper. The script additionally contains various wrapper scripts around compression that we used for the project so feel free to check out the source code.

# Requirements

General
- All scripts tested on Ubuntu 16.04 and 18.04
- python3
- [tqdm](https://github.com/tqdm/tqdm) (install via pip install tqdm)

For compression/extraction
- [ffmpeg built with h264](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
- opencv (install via  pip install opencv-python)


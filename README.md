# FaceForensics++: Learning to Detect Manipulated Facial Images

![Header](images/teaser.png)

## Overview
FaceForensics++ is a forensics dataset consisting of 1000 original video sequences that have been manipulated with four automated face manipulation methods: Deepfakes, Face2Face, FaceSwap and NeuralTextures. The data has been sourced from 977 youtube videos and all videos contain a trackable mostly frontal face without occlusions which enables automated tampering methods to generate realistic forgeries. As we provide binary masks the data can be used for image and video classification as well as segmentation. In addition, we provide 1000 Deepfakes models to generate and augment new data.



For more information, please consult [our updated paper](https://arxiv.org/abs/1901.08971).

## What is new

<p align="center">
  <img width="460" height="300" src="images/DDD_samples.gif">
</p>

- __[Deep Fake Detection Dataset](https://ai.googleblog.com/2019/09/contributing-data-to-deepfake-detection.html):__ We are hosting the Deep Fake Detection Dataset provided by Google & JigSaw. The dataset contains over 3000 manipulated videos from 28 actors in various scenes. The dataset has a similar file structure and is downloaded by default together with the regular dataset. See the [dataset](dataset) page for more information. 

- __Neural Textures:__ We included a fourth manipulation method that does face manipulation using GANs and [Neural Textures](https://arxiv.org/pdf/1904.12356.pdf). All results have been updated to incorporate the new manipulation method and we have updated the benchmark as well. We refer to the paper for more information.
Unfortunately, we won't continue support on the old benchmark after this update, though you can still submit your models to the new benchmark by creating a new submission.

## Access
If you would like to download the FaceForensics++ dataset, please fill out [this google form](https://docs.google.com/forms/d/e/1FAIpQLSdRRR3L5zAv6tQ_CKxmK4W96tAab_pfBu2EKAgQbeDVhmXagg/viewform) and, once accepted, we will send you the link to our download script.

If you have not received a response within a week, it is likely that your email is bouncing - please check this before sending repeat requests.

Once, you obtain the download link, please head to the [download section](dataset/README.md). You can also find details about the generation of the dataset there.

## [Benchmark](http://kaldir.vc.in.tum.de/faceforensics_benchmark/)
We are offering an [automated benchmark](http://kaldir.vc.in.tum.de/faceforensics_benchmark/) for facial manipulation detection on the presence of compression based on our manipulation methods that contains 1000 images. If you are interested to test your approach on unseen data, check it out! For more information, please consult [our paper](https://arxiv.org/abs/1901.08971). You can download the benchmark images [here](http://kaldir.vc.in.tum.de/faceforensics_benchmark_images.zip).


## Original FaceForensics
You can view the original FaceForensics github [here](https://github.com/ondyari/FaceForensics/tree/original). Any request to this dataset will also contain the download link to the original version of our dataset. 


## Citation
If you use the FaceForensics++ data or code please cite:
```
@inproceedings{roessler2019faceforensicspp,
	author = {Andreas R\"ossler and Davide Cozzolino and Luisa Verdoliva and Christian Riess and Justus Thies and Matthias Nie{\ss}ner},
	title = {Face{F}orensics++: Learning to Detect Manipulated Facial Images},
	booktitle= {International Conference on Computer Vision (ICCV)},
	year = {2019}
}

```

## Help
If you have any questions, please contact us at [faceforensics@googlegroups.com](faceforensics@googlegroups.com).

## Video
Please view our youtube video [here](https://www.youtube.com/watch?v=x2g48Q2I2ZQ).

[![youtubev_video](https://img.youtube.com/vi/x2g48Q2I2ZQ/0.jpg)](https://www.youtube.com/watch?v=x2g48Q2I2ZQ)

## Changelog
23.09.2019: Added sample videos as well as the Deep Fake Detection Dataset

30.08.2019: Paper got accepted to ICCV 2019! Updated the download script to include NeuralTextures and changed instructions

06.04.2019: Updated sample and added benchmark

02.04.2019: Updated our arxiv paper, switched to google forms, release of dataset generation methods and added a classification sample

25.01.2019: Release of FaceForensics++

## License
The data is released under the [FaceForensics Terms of Use](http://kaldir.vc.in.tum.de/faceforensics_tos.pdf), and the code is released under the MIT license.

Copyright (c) 2019

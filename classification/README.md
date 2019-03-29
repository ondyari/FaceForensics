# Classification

XceptionNet from our paper trained on our FaceForensics++ dataset. Besides the full image models, all models were trained on slightly enlarged face crops with a scale factor of 1.3.
The models were trained using the Face2Face face tracker, though the `detect_from_models.py` file uses the freely available dlib face detector.

Note that we provide the trained models from our paper which have not been fine-tuned for general compressed videos. You can find our used models under [this link](http://kaldir.vc.in.tum.de:/FaceForensics/models/faceforensics++_models.zip). The   

Setup:
- Install required modules via `requirement.txt` file
- Run detection from a single video file or folder with
```shell
python detect_from_video.py
-i <path to input video or folder of videos with extenstion '.mp4' or '.avi'>
-m <path to model file, default is imagenet model
-o <path to output folder, will contain output video(s)
```  
from the classification folder. Enable cuda with ```--cuda```  or see parameters with ```python detect_from_video.py -h```.



# Requirements

- python 3.6
- requirements.txt

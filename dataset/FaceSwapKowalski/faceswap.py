"""
FaceSwap single image sequence manipulation script

Usage: see -h or https://github.com/ondyari/FaceForensics/datasets/manipulation_methods

Author: Andreas Roessler
Date: 23.02.2019
"""
import dlib
import cv2
import numpy as np
import os
from os.path import join
import progressbar
import argparse
import sys
import contextlib


@contextlib.contextmanager
def redirect_stdout(target):
    original = sys.stdout
    sys.stdout = target
    yield
    sys.stdout = original


# Suppress "hello pygame" message
with redirect_stdout(open(os.devnull, 'w')):
    import FaceSwap.models as models
    import FaceSwap.NonLinearLeastSquares as NonLinearLeastSquares
    import FaceSwap.ImageProcessing as ImageProcessing
    from FaceSwap.drawing import *
    import FaceSwap.FaceRendering as FaceRendering
    import FaceSwap.utils as utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source_folder', '-i1', type=str,
                        help='Source input folder filename, expects images of'
                             'form "%04d.png". (Replaces faces of this '
                             'sequence)')
    parser.add_argument('--target_folder', '-i2', type=str,
                        help='Source input folder filename, expects images of'
                             'form "%04d.png". (Faces are extracted  of this '
                             'sequence)')
    parser.add_argument('--output_folder', '-o', type=str,
                        default='output/images',
                        help='Output image folder.')
    parser.add_argument('--output_mask_folder', '-mo', type=str,
                        default='output/masks',
                        help='Output mask folder.')
    parser.add_argument('--max_frames', type=int,
                        default=9000,
                        help='Maximum number of frames, will not extract any '
                             'more frames after reaching this number. 9000 is ' 
                             ' chosen simply because of the fact that there is '
                             'no video in our dataset with longer length.')
    config, _ = parser.parse_known_args()

    # Load face detector and landmarks predictor
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    maxImageSizeForDetection = 480
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)

    # Load 3d shape models
    mean3DShape, blendshapes, mesh, idxs3D, idxs2D = \
        utils.load3DFaceModel("candide.npz")

    # Get maximum number of manipulation frames
    source_folder = config.source_folder
    target_folder = config.target_folder
    num_frames_source = len(os.listdir(source_folder))
    num_frames_target = len(os.listdir(target_folder))
    max_frames = min(num_frames_source, num_frames_target, config.max_frames)

    # Create output folders
    output_folder = config.output_folder
    output_mask_folder = config.output_mask_folder
    for folder in [output_folder, output_mask_folder]:
        try:
            os.makedirs(folder)
        except:
            pass

    # Loop
    bar = progressbar.ProgressBar(max_value=max_frames)
    bar.start()
    frame_number = 0
    target_pointX = -1
    target_pointY = -1
    source_pointX = -1
    source_pointY = -1

    while True:
        image_fn = '{:04d}.png'.format(frame_number)
        for f in [join(source_folder, image_fn), join(target_folder, image_fn)]:
            if not os.path.isfile(f):
                break

        source_img = cv2.imread(join(source_folder, image_fn))
        target_img = cv2.imread(join(target_folder, image_fn))
        renderedImg = 0*target_img
        swapped_img = np.copy(target_img)

        projectionModel = models.OrthographicProjectionBlendshapes(
            blendshapes.shape[0])
        modelParams = None

        source_shapes2D = utils.getFaceKeypoints(source_img, detector,
                                                 predictor,
                                                 maxImageSizeForDetection)
        target_shapes2D = utils.getFaceKeypoints(target_img, detector,
                                                 predictor,
                                                 maxImageSizeForDetection)

        if (source_shapes2D is not None) and (target_shapes2D is not None):
            if len(source_shapes2D) == 1:
                source_shape2D_index = 0
            elif source_pointX < 0:
                source_shape2D_index = [np.max(shape2D[0]) - np.min(shape2D[0])
                                        for shape2D in source_shapes2D]
                source_shape2D_index = np.argmax(source_shape2D_index)
            else:
                source_shape2D_index = np.argmin(
                    [np.min(np.abs(shape2D[0]-source_pointX)
                            + np.abs(shape2D[1]-source_pointY))
                     for shape2D in source_shapes2D])

            if len(target_shapes2D) == 1:
                target_shape2D_index = 0
            elif target_pointX<0:
                target_shape2D_index = [np.max(shape2D[0]) - np.min(shape2D[0])
                                        for shape2D in target_shapes2D]
                target_shape2D_index = np.argmax(target_shape2D_index)
            else:
                target_shape2D_index = np.argmin(
                    [np.min(np.abs(shape2D[0]-target_pointX) +
                            np.abs(shape2D[1]-target_pointY))
                     for shape2D in target_shapes2D])

            source_shape2D = source_shapes2D[source_shape2D_index]
            source_pointX = np.mean(source_shape2D[0])
            source_pointY = np.mean(source_shape2D[1])

            shape2D = target_shapes2D[target_shape2D_index]
            target_pointX = np.mean(shape2D[0])
            target_pointY = np.mean(shape2D[1])

            textureCoords = utils.getShapeTextureCoords(
                source_shape2D, mean3DShape, blendshapes, idxs2D, idxs3D)
            renderer = FaceRendering.FaceRenderer(
                target_img, source_img, textureCoords, mesh)

            # 3D model parameter initialization
            modelParams = projectionModel.getInitialParameters(
                mean3DShape[:, idxs3D], shape2D[:, idxs2D])
            # 3D model parameter optimization
            modelParams = NonLinearLeastSquares.GaussNewton(
                modelParams, projectionModel.residual, projectionModel.jacobian,
                ([mean3DShape[:, idxs3D],
                  blendshapes[:, :, idxs3D]], shape2D[:, idxs2D]), verbose=0)

            # rendering the model to an image
            shape3D = utils.getShape3D(mean3DShape, blendshapes, modelParams)
            renderedImg = renderer.render(shape3D)

            # blending of the rendered face with the image
            mask = np.any(renderedImg>0,-1)
            renderedImg = ImageProcessing.colorTransfer(target_img, renderedImg,
                                                        mask)
            swapped_img = ImageProcessing.blendImages(renderedImg, swapped_img,
                                                      mask)
        # Save files
        cv2.imwrite(join(output_mask_folder, image_fn), renderedImg)
        cv2.imwrite(join(output_folder, image_fn), swapped_img)

        # Misc
        frame_number += 1
        if frame_number >= max_frames:
            break
        bar.update(frame_number)
    # End progressbar
    bar.finish()

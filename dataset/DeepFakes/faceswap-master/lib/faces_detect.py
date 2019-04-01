#!/usr/bin python3
""" Face and landmarks detection for faceswap.py """

from lib import face_alignment
import numpy as np


# Static variable wrapper
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def compute_center(landmarks):
    x, y, w, h = landmarks[0][:4]
    return x + 0.5*w, y + 0.5 * h


@static_vars(prev_center=None)
def detect_faces(frame, detector, verbose, rotation=0, mtcnn_kwargs=None):
    """ Detect faces and draw landmarks in an image """
    face_detect = face_alignment.Extract(frame,
                                         detector,
                                         mtcnn_kwargs,
                                         verbose)
    # --- Changes ---
    # If we have a center, take the face that is closest to previous center
    if detect_faces.prev_center is None:
        print('WARNING: Static variable in detect_faces, only extract one '
              'sequence per faceswap.py call')
        # Find biggest face by looking at y bounding box size, 0 is biggest
        detect_landmarks = face_detect.landmarks
        detect_landmarks = sorted(detect_landmarks,
                                  key=lambda x: x[0][1] - x[0][3])
        face_detect.landmarks = [detect_landmarks[0]]
    else:
        closest = float('inf')
        closest_face_idx = -1
        closest_center = None
        for i, landmark in enumerate(face_detect.landmarks):
            center = compute_center(landmark)
            length = np.linalg.norm(np.array(center) -
                                    np.array(detect_faces.prev_center))
            if length < closest:
                closest = length
                closest_face_idx = i
                closest_center = center
        detect_faces.prev_center = closest_center
        face_detect.landmarks = [face_detect.landmarks[closest_face_idx]]
    detect_faces.prev_center = compute_center(face_detect.landmarks[0])
    # --- Changes ---

    for face in face_detect.landmarks:
        ax_x, ax_y = face[0][0], face[0][1]
        right, bottom = face[0][2], face[0][3]
        landmarks = face[1]

        yield DetectedFace(frame[ax_y: bottom, ax_x: right],
                           rotation,
                           ax_x,
                           right - ax_x,
                           ax_y,
                           bottom - ax_y,
                           landmarksXY=landmarks)


class DetectedFace(object):
    """ Detected face and landmark information """
    def __init__(self, image=None, r=0, x=None,
                 w=None, y=None, h=None, landmarksXY=None):
        self.image = image
        self.r = r
        self.x = x
        self.w = w
        self.y = y
        self.h = h
        self.landmarksXY = landmarksXY

    def landmarks_as_xy(self):
        """ Landmarks as XY """
        return self.landmarksXY

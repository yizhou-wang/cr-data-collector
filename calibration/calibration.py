'''
camera calibration for distorted images with chess board samples
reads distorted images, calculates the calibration and write undistorted images
usage:
    calibrate.py [--debug <output path>] [--square_size] [<image mask>]
default values:
    --debug:    ./output/
    --square_size: 1.0
    <image mask> defaults to ../data/left*.jpg
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import os
import sys
import cv2
import yaml

    
'''
Find and return chessboard and corners of the image.
Not Found chessboard in the image : return None.
'''

def camera_calibration(base_dir, img_names, pattern_size=(8, 6), square_size=0.022):
    h, w = cv2.imread(os.path.join(base_dir, img_names[0]), cv2.IMREAD_GRAYSCALE).shape[:2]
    print('calibration image size (w, h): (%d, %d)' % (w, h))

    corners_list = []
    pattern_points_list = []
    for img_name in img_names:
        img_name = os.path.join(base_dir, img_name)
        chessboard = chessboard_from_img(img_name, pattern_size, square_size)
        if chessboard is not None:
            corners, pattern_points = chessboard
            # print(corners.shape)
            # print(pattern_points.shape)
            corners_list.append(corners)
            pattern_points_list.append(pattern_points)

    if len(corners_list) > 20:
        print("%d valid images detected!" % len(corners_list))
    else:
        print("%d valid images detected! Not enough for calibration!" % len(corners_list))
        return None

    # print(len(corners_list))
    # print(len(pattern_points_list))

    # calculate camera parameters
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(
        pattern_points_list, corners_list, (w, h), None, None)

    return w, h, camera_matrix, dist_coefs, rvecs, tvecs


def chessboard_from_img(img_name, pattern_size, square_size): 
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("Failed to load ", img_name)
        return None

    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size
    w = img.shape[1] 
    h = img.shape[0]
    # assert w == img.shape[1] and h == img.shape[0], ("size: %d x %d ... " % (img.shape[1], img.shape[0]))

    found, corners = cv2.findChessboardCorners(img, pattern_size)
    ### return all the inner corners of the chessboard. If it fails to return all the
    ### inner corners or error occurs, then it return zero.
    ### pattern_size : (number of corners_per column, number of corners_per row).
    ### Check for the meaning of pattern_size.

    if not found:
        print('%s: chessboard not found' % img_name)
        return None

    print('%s: chessboard is found' % img_name)
    term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
    cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
        
    return (corners.reshape(-1, 2), pattern_points)
  

def save_cam_calib_yaml(yaml_name, w, h, camera_matrix, dist_coefs, rvecs, tvecs):

    camera_matrix = camera_matrix.round(decimals=6)
    camera_matrix_yaml = np.reshape(camera_matrix, [9, ]).tolist()
    dist_coefs = dist_coefs.round(decimals=6)
    dist_coefs_yaml = np.reshape(dist_coefs, [5, ]).tolist()

    d = {
        'image_width': w,
        'image_height': h,
        'camera_matrix': {
            'rows': camera_matrix.shape[0],
            'cols': camera_matrix.shape[1],
            'data': camera_matrix_yaml
        },
        'dis_coefs': {
            'rows': dist_coefs.shape[0],
            'cols': dist_coefs.shape[1],
            'data': dist_coefs_yaml
        }
    }

    with open(yaml_name, 'w') as outfile:
        yaml.dump(d, outfile, default_flow_style=None, sort_keys=False)
  

if __name__ == '__main__':
    # Test of the result. Main program.
    # D:\RawData\2019_05_02\2019_05_02_calib001\images
    base_dir = "D:\\RawData\\2019_05_02\\2019_05_02_calib\\images"
    img_names = sorted(os.listdir(base_dir))
    camera_calibration(base_dir, img_names)
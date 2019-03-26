import os
import numpy as np
import cv2
import yaml
import datetime


def load_calib(calib_yaml):
    with open(calib_yaml, "r") as stream:
        data = yaml.safe_load(stream)
        image_width = data['image_width']
        image_height = data['image_height']
        camera_matrix = data['camera_matrix']
        distortion_coefficients = data['distortion_coefficients']
        rectification_matrix = data['rectification_matrix']
        projection_matrix = data['projection_matrix']

        K = np.array(camera_matrix['data'])
        K = np.reshape(K, (camera_matrix['rows'], camera_matrix['cols']))
        D = np.array(distortion_coefficients['data'])
        D = np.reshape(D, (distortion_coefficients['rows'], distortion_coefficients['cols']))
        D = np.squeeze(D)

    return image_width, image_height, K, D


def undistort(im_name, K, D):

    im = cv2.imread(im_name)
    undistort = cv2.undistort(im, K, D)

    return undistort


def undistort_for_seq(folder_dir, calib_yaml):

    im_names = sorted(os.listdir(folder_dir))
    w, h, K, D = load_calib(calib_yaml)
    folder_out_dir = folder_dir.replace('images', 'images_udst')

    if not os.path.exists(folder_out_dir):
        os.makedirs(folder_out_dir)

    for im_name in im_names:
        im_dir = os.path.join(folder_dir, im_name)
        im_undis = undistort(im_dir, K, D)
        im_out_name = os.path.join(folder_out_dir, im_name)
        cv2.imwrite(im_out_name, im_undis)


def undistort_for_date(date, data_dir='D:\RawData'):

    base_dir = os.path.join(data_dir, date)

    if not os.path.exists(base_dir):
        raise ValueError("Data not found!")

    calib_yaml = os.path.join(base_dir, 'ost.yaml')
    if not os.path.exists(calib_yaml):
        print("Specific calibration for this date is unavailable, using default value.\n")
        calib_yaml = 'ost.yaml'
    seqs = sorted(os.listdir(base_dir))
    for seq in seqs:
        folder_dir = os.path.join(base_dir, seq, 'images')
        print("Undistorting %s ..." % folder_dir)
        undistort_for_seq(folder_dir, calib_yaml)

    print("\nUndistortion finished for date %s." % date)


if __name__ == '__main__':

    # main("D:/RawData/0000/images", 'ost.yaml')
    # load_calib('ost.yaml')

    date = input("Enter date (default=today): ")
    if date == '':
        now = datetime.datetime.now()
        date = "%s_%s_%s" % (now.year, now.month, now.day)

    undistort_for_date(date)

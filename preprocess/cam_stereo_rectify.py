import os
import numpy as np
import cv2
import yaml
import datetime

from skimage.color import rgb2hsv, hsv2rgb
from skimage import exposure
import matplotlib.pyplot as plt

from color_transfer import color_transfer


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
        R = np.array(rectification_matrix['data'])
        R = np.reshape(R, (rectification_matrix['rows'], rectification_matrix['cols']))
        P = np.array(projection_matrix['data'])
        P = np.reshape(P, (projection_matrix['rows'], projection_matrix['cols']))

    return image_width, image_height, K, D, R, P


def undistort(im_name, K, D):

    im = cv2.imread(im_name)
    undistort = cv2.undistort(im, K, D)

    return undistort


def hist_equal(img):
    img = rgb2hsv(img)
    brightness = img[:,:,2].copy()
    brightness = (brightness * 255).astype(np.uint8)
    brightness = exposure.equalize_adapthist(brightness, clip_limit=0.03)
    img[:,:,2] = brightness.astype(np.float32)
    img = hsv2rgb(img)
    return img


def rectify_for_seq(folder_dir_l, folder_dir_r, calib_yaml_l, calib_yaml_r):

    im_names_l = sorted(os.listdir(folder_dir_l))
    w_l, h_l, K_l, D_l, R_l, P_l = load_calib(calib_yaml_l)
    folder_out_dir_l = folder_dir_l.replace('images_raw', 'images')
    im_names_r = sorted(os.listdir(folder_dir_r))
    w_r, h_r, K_r, D_r, R_r, P_r = load_calib(calib_yaml_r)
    folder_out_dir_r = folder_dir_r.replace('images_raw', 'images')

    assert len(im_names_l) == len(im_names_r)
    assert w_l == w_r
    assert h_l == h_r

    if not os.path.exists(folder_out_dir_l):
        os.makedirs(folder_out_dir_l)
    if not os.path.exists(folder_out_dir_r):
        os.makedirs(folder_out_dir_r)

    #computes undistort and rectify maps
    mapxL, mapyL = cv2.initUndistortRectifyMap(K_l, D_l, R_l, P_l, (w_l, h_l), cv2.CV_32FC1)
    mapxR, mapyR = cv2.initUndistortRectifyMap(K_r, D_r, R_r, P_r, (w_r, h_r), cv2.CV_32FC1)

    for im_name_l, im_name_r in zip(im_names_l, im_names_r):
        im_dir_l = os.path.join(folder_dir_l, im_name_l)
        im_dir_r = os.path.join(folder_dir_r, im_name_r)

        lFrame = cv2.imread(im_dir_l)
        rFrame = cv2.imread(im_dir_r)
        dstL = cv2.remap(lFrame, mapxL, mapyL,cv2.INTER_LINEAR)
        dstR = cv2.remap(rFrame, mapxR, mapyR,cv2.INTER_LINEAR)
        dstL = dstL[:int(0.8*h_l), :, :]
        dstR = dstR[:int(0.8*h_r), :, :]

        dstL = hist_equal(dstL)
        dstR = hist_equal(dstR)
        dstL = (dstL * 255).astype(np.uint8)
        dstR = (dstR * 255).astype(np.uint8)
        dstL = color_transfer(dstR, dstL)

        im_out_name_l = os.path.join(folder_out_dir_l, im_name_l)
        im_out_name_r = os.path.join(folder_out_dir_r, im_name_r)
        cv2.imwrite(im_out_name_l, dstL)
        cv2.imwrite(im_out_name_r, dstR)


def rectify_for_date(date, data_dir='D:\\RawData'):

    base_dir = os.path.join(data_dir, date)

    if not os.path.exists(base_dir):
        raise ValueError("Data not found!")

    # calib_yaml = os.path.join(base_dir, 'cam_calib.yaml')
    # if not os.path.exists(calib_yaml):
    #     print("Specific calibration for this date is unavailable, using default value.\n")
    #     calib_yaml = 'ost.yaml'

    calib_yaml_l = os.path.join(data_dir, 'calib', date + '_18384019-19325055', 'left.yaml')
    calib_yaml_r = os.path.join(data_dir, 'calib', date + '_18384019-19325055', 'right.yaml')
    # calib_yaml_l = os.path.join(data_dir, 'calib', '2019_09_29_18384019-19325055', 'left.yaml')
    # calib_yaml_r = os.path.join(data_dir, 'calib', '2019_09_29_18384019-19325055', 'right.yaml')
    seqs = sorted(os.listdir(base_dir))
    # seqs = ['2019_09_29_onrd038']
    for seq in seqs:
        folder_dir_l = os.path.join(base_dir, seq, 'images_raw_0')
        folder_dir_r = os.path.join(base_dir, seq, 'images_raw_1')
        print("Rectifying %s ..." % folder_dir_l)
        rectify_for_seq(folder_dir_l, folder_dir_r, calib_yaml_l, calib_yaml_r)

    print("\nStereo rectification finished for date %s." % date)


if __name__ == '__main__':

    # main("D:/RawData/0000/images", 'ost.yaml')
    # load_calib('ost.yaml')

    data_root = input("Enter root directory (default=D:\\RawData): ")
    if data_root == '':
        data_root = 'D:\\RawData'
        # data_root = '/mnt/nas_crdataset2'
    date = input("Enter date (default=today): ")
    if date == '':
        now = datetime.datetime.now()
        date = "%s_%02d_%02d" % (now.year, now.month, now.day)
        # date = "2019_10_13"

    rectify_for_date(date, data_dir=data_root)

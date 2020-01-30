import os
import sys
import numpy as np
import cv2
import yaml
import datetime
import argparse
import shutil

from skimage.color import rgb2hsv, hsv2rgb
from skimage import exposure

sys.path.append(os.path.abspath('..'))
from color_transfer import color_transfer
from utils.dataset_tools import calculate_frame_offset


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocessing for videos')
    parser.add_argument('--src_root', type=str, help='source data root directory')
    parser.add_argument('--dst_root', type=str, help='destination data root directory')
    parser.add_argument('--dates', type=str, default='', help='process dates (separate by comma)')
    parser.add_argument('--overwrite', action="store_true", help='whether rewrite if exist')
    parser.add_argument('--trim', action="store_true", help='whether trim video according to radar data')
    args = parser.parse_args()
    return args


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


def rectify_for_seq(folder_dir_l, folder_dir_r, folder_dir_l_new, folder_dir_r_new, calib_yaml_l, calib_yaml_r,
                    startid, nframes, overwrite=False):

    im_names_l = sorted(os.listdir(folder_dir_l))[startid:startid+nframes]
    w_l, h_l, K_l, D_l, R_l, P_l = load_calib(calib_yaml_l)
    # folder_out_dir_l = folder_dir_l.replace('images_raw', 'images')
    folder_out_dir_l = folder_dir_l_new
    im_names_r = sorted(os.listdir(folder_dir_r))[startid:startid+nframes]
    w_r, h_r, K_r, D_r, R_r, P_r = load_calib(calib_yaml_r)
    # folder_out_dir_r = folder_dir_r.replace('images_raw', 'images')
    folder_out_dir_r = folder_dir_r_new

    assert len(im_names_l) == len(im_names_r)
    assert w_l == w_r
    assert h_l == h_r

    if overwrite and os.path.exists(folder_out_dir_l):
        shutil.rmtree(folder_out_dir_l)
    if overwrite and os.path.exists(folder_out_dir_r):
        shutil.rmtree(folder_out_dir_r)
    if not os.path.exists(folder_out_dir_l):
        os.makedirs(folder_out_dir_l)
    if not os.path.exists(folder_out_dir_r):
        os.makedirs(folder_out_dir_r)

    # computes undistort and rectify maps
    mapxL, mapyL = cv2.initUndistortRectifyMap(K_l, D_l, R_l, P_l, (w_l, h_l), cv2.CV_32FC1)
    mapxR, mapyR = cv2.initUndistortRectifyMap(K_r, D_r, R_r, P_r, (w_r, h_r), cv2.CV_32FC1)

    for idx_new, (im_name_l, im_name_r) in enumerate(zip(im_names_l, im_names_r)):
        im_dir_l = os.path.join(folder_dir_l, im_name_l)
        im_dir_r = os.path.join(folder_dir_r, im_name_r)
        im_out_name_l = os.path.join(folder_out_dir_l, '%010d.jpg' % idx_new)
        im_out_name_r = os.path.join(folder_out_dir_r, '%010d.jpg' % idx_new)

        lFrame = cv2.imread(im_dir_l)
        rFrame = cv2.imread(im_dir_r)
        dstL = cv2.remap(lFrame, mapxL, mapyL,cv2.INTER_LINEAR)
        dstR = cv2.remap(rFrame, mapxR, mapyR,cv2.INTER_LINEAR)
        dstL = dstL[:int(0.8*h_l), :, :]
        dstR = dstR[:int(0.8*h_r), :, :]

        # dstL = hist_equal(dstL)
        # dstR = hist_equal(dstR)
        # dstL = (dstL * 255).astype(np.uint8)
        # dstR = (dstR * 255).astype(np.uint8)
        dstL = color_transfer(dstR, dstL)

        cv2.imwrite(im_out_name_l, dstL)
        cv2.imwrite(im_out_name_r, dstR)


def rectify_for_date(date, data_dir='D:\\RawData', data_dir_new='D:\\RawData', overwrite=False, trim=True):

    base_dir = os.path.join(data_dir, date)
    base_dir_new = os.path.join(data_dir_new, date)

    if not os.path.exists(base_dir):
        raise ValueError("Data not found!")

    # calib_yaml = os.path.join(base_dir, 'cam_calib.yaml')
    # if not os.path.exists(calib_yaml):
    #     print("Specific calibration for this date is unavailable, using default value.\n")
    #     calib_yaml = 'ost.yaml'

    calib_yaml_l = os.path.join(data_dir, 'calib', date + '_18384019-19325055', 'left.yaml')
    calib_yaml_r = os.path.join(data_dir, 'calib', date + '_18384019-19325055', 'right.yaml')
    if not os.path.exists(calib_yaml_l):
        calib_yaml_l = os.path.join(data_dir, 'calib', '2019_09_29_18384019-19325055', 'left.yaml')
        calib_yaml_r = os.path.join(data_dir, 'calib', '2019_09_29_18384019-19325055', 'right.yaml')
    seqs = sorted(os.listdir(base_dir))
    # seqs = ['2019_09_29_onrd038']
    for seq in seqs:
        print("Preprocessing sequence: %s ..." % seq)

        folder_dir_l = os.path.join(base_dir, seq, 'images_raw_0')
        folder_dir_r = os.path.join(base_dir, seq, 'images_raw_1')
        folder_dir_l_new = os.path.join(base_dir_new, seq, 'images_0')
        folder_dir_r_new = os.path.join(base_dir_new, seq, 'images_1')

        if trim:
            if 'onrd' in seq:
                frame_exp = 40
            else:
                frame_exp = 0
            start_time_txt = os.path.join(base_dir, seq, 'start_time_h.txt')
            offsetrc, _, _ = calculate_frame_offset(start_time_txt)
            nframes_raw = len(os.listdir(folder_dir_r))
            nframes = nframes_raw - frame_exp - offsetrc
            startid_cam = frame_exp
        else:
            startid_cam = 0
            nframes = len(os.listdir(folder_dir_r))

        print("StartID: %d | FrameNum: %d" % (startid_cam, nframes))
        rectify_for_seq(folder_dir_l, folder_dir_r, folder_dir_l_new, folder_dir_r_new, calib_yaml_l, calib_yaml_r,
                        startid_cam, nframes, overwrite)


if __name__ == '__main__':

    # main("D:/RawData/0000/images", 'ost.yaml')
    # load_calib('ost.yaml')

    # data_root = input("Enter root directory (default=D:\\RawData): ")
    # if data_root == '':
    #     data_root = 'D:\\RawData'
    #     # data_root = '/mnt/nas_crdataset2'
    # date = input("Enter date (default=today): ")

    args = parse_args()
    data_root = args.src_root
    data_root_new = args.dst_root
    dates = args.dates
    overwrite = args.overwrite
    trim = args.trim
    if dates == '':
        now = datetime.datetime.now()
        dates = ["%s_%02d_%02d" % (now.year, now.month, now.day)]
    else:
        dates = dates.split(',')

    for date in dates:
        print("Preprocessing videos for date: %s ..." % date)
        rectify_for_date(date, data_dir=data_root, data_dir_new=data_root_new, overwrite=overwrite, trim=trim)

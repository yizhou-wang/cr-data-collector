# coding=utf-8
import os
import shutil
import time
import datetime
import camera_calibration as calib


def calib_for_date(date, data_dir='D:\\RawData'):
    
    base_dir = os.path.join(data_dir, date)
    img_dir =os.path.join(base_dir, date+'_calib', 'images')

    if not os.path.exists(img_dir):
        raise ValueError("Data not found!")

    img_names = sorted(os.listdir(img_dir))

    w, h, camera_matrix, dist_coefs, rvecs, tvecs = calib.camera_calibration(img_dir, img_names)

    print("Camera calibration finished! Saving results...")

    yaml_name = os.path.join(base_dir, 'cam_calib.yaml')
    calib.save_cam_calib_yaml(yaml_name, w, h, camera_matrix, dist_coefs, rvecs, tvecs)


if __name__ == '__main__':

    date = input("Enter date (default=today): ")
    if date == '':
        now = datetime.datetime.now()
        date = "%s_%02d_%02d" % (now.year, now.month, now.day)

    calib_for_date(date)

import os
import numpy as np
import csv
import json
import yaml
import math
import scipy
import cv2

from scipy.optimize import least_squares

DATA_DIR = "/mnt/disk2/CR_dataset"
DATE = "2019_05_24"
SEQs = ["2019_05_24_cali002", "2019_05_24_cali003"]
FULL_PATHs = [os.path.join(DATA_DIR, DATE, seq) for seq in SEQs]


def ra2xy(r, a):
    x = r * np.sin(a)
    y = r * np.cos(a)
    return x, y


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


def detect_reflector(base_dir, img_name, read_from_file=True):
    """
    Detect reflection corner in image.
    img_name: image name
    :return: 2D points in pixel coordinates
    """
    img_index = img_name.split('.')[0]
    if read_from_file:
        reflector_dets_file = os.path.join(base_dir, 'reflector_dets', img_index+'.txt')
        if not os.path.exists(reflector_dets_file):
            print("%s: reflector detection file does not exists!" % img_name)
            return None
        load_reflector_dets_csv(reflector_dets_file, n_points=4)


def load_reflector_dets_txt(filename, n_points=6):

    # detection file format:
    # each 2D point in one line: (x, y), where x for width, y for height
    # order should from left to right and then from up to down
    with open(filename, 'r') as f:
        data = f.readlines()
    points_2d = []
    for line in data:
        if line is None:
            continue
        l_str = line.rstrip().split()
        assert len(l_str) == 2, "wrong format for 2D point detections!"
        x = int(float(l_str[0]))
        y = int(float(l_str[1]))
        points_2d.append(np.array([x, y]))

    assert len(points_2d) == n_points

    points_2d = np.array(points_2d)

    return points_2d


def load_reflector_dets_csv(filename, n_points=6, distort=False):

    headers = None
    centers = np.zeros((n_points, 2))
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                headers = row
                line_count += 1
            else:
                region_count = int(float(row[3]))
                if region_count != n_points:
                    continue
                region_id = int(float(row[4]))
                region_shape_attributes = json.loads(row[5])
                region_attributes = json.loads(row[6])
                if (distort and region_attributes['distort'] == 'true') or \
                    (not distort and region_attributes['distort'] == 'false'):
                    x = region_shape_attributes['x']
                    y = region_shape_attributes['y']
                    w = region_shape_attributes['width']
                    h = region_shape_attributes['height']
                    center_x = x + w / 2.0
                    center_y = y + h / 2.0
                    centers[region_id, 0] = center_x
                    centers[region_id, 1] = center_y

                line_count += 1

    return centers


def load_cam_dets_all(filenames, n_points=4, file_format='csv'):

    points_2d = np.zeros((len(filenames) * n_points, 2))

    for f_id, filename in enumerate(filenames):
        if file_format == 'csv':
            filename = os.path.join(filename, filename.split('/')[-1]+'.csv')
            points_2d[f_id*n_points:(f_id+1)*n_points, :] = load_reflector_dets_csv(filename, n_points=n_points)
        if file_format == 'txt':
            filename = os.path.join(filename, filename.split('/')[-1]+'.txt')
            points_2d[f_id*n_points:(f_id+1)*n_points, :] = load_reflector_dets_txt(filename, n_points=n_points)

    return points_2d


def load_radar_dets_txt(filename, n_points=6):

    # detection file format:
    # each 2D point in one line: (r, a), where r for range, a for angle
    # order should from left to right and then from up to down
    with open(filename, 'r') as f:
        data = f.readlines()
    points_2d = np.zeros((n_points, 2))
    for line in data:
        if line is None:
            continue
        l_str = line.rstrip().split('\t')
        assert len(l_str) == 3, "len(l_str) = %d, wrong format for 2D point detections!" % len(l_str)
        point_id = int(float(l_str[0])) - 1
        a_rad = math.radians(float(l_str[1]))
        r = float(l_str[2])
        x, y = ra2xy(r, a_rad)
        points_2d[point_id, 0] = x
        points_2d[point_id, 1] = y

    return points_2d


def load_radar_dets_all(filenames, n_points=4, file_format='txt'):

    points_2d = np.zeros((len(filenames) * n_points, 2))

    for f_id, filename in enumerate(filenames):
        # if file_format == 'csv':
        #     filename = os.path.join(filename, 'radar_dets.csv')
        #     points_2d[f_id*n_points:(f_id+1)*n_points, :] = load_radar_dets_csv(filename, n_points=n_points)
        if file_format == 'txt':
            filename = os.path.join(filename, 'radar_dets.txt')
            points_2d[f_id*n_points:(f_id+1)*n_points, :] = load_radar_dets_txt(filename, n_points=n_points)

    return points_2d


def generate_points_3d(pattern_size=(2, 2), square_size=2):
    # order should from left to right and then from up to down
    n_rows = pattern_size[0]
    n_cols = pattern_size[1]
    points_3d = np.zeros((n_rows*n_cols, 3))
    for r in range(n_rows):
        for c in range(n_cols):
            points_3d[r*n_cols+c, 0] = c * square_size
            points_3d[r*n_cols+c, 1] = r * square_size
    return points_3d


def homo(points_3d):
    if points_3d.shape[1] < 3 or points_3d.shape[1] > 4:
        raise
    if points_3d.shape[1] == 4:
        return points_3d

    n_points = points_3d.shape[0]
    pad = np.ones((n_points, 1))
    points_3d_homo = np.concatenate((points_3d, pad), axis=1)
    return points_3d_homo


def reproj_error(transform_vec, K, points_2d, points_3d):

    rot_vec = transform_vec[:3]
    t_vec = transform_vec[3:]
    rot_mat, _ = cv2.Rodrigues(rot_vec)
    transform_mat = np.concatenate((rot_mat, np.reshape(t_vec, (3, 1))), axis=1)
    P = np.dot(K, transform_mat)
    points_2d_proj = np.dot(P, homo(points_3d).T).T
    down = np.tile(points_2d_proj[:, -1:], (1, 3))
    points_2d_proj = points_2d_proj / down
    error = np.linalg.norm(points_2d_proj[:, :2] - points_2d, axis=1)

    return np.sum(error)


def reproj_error_radar(transform_vec, A, points_2d, points_3d):

    rot_vec = transform_vec[:3]
    t_vec = transform_vec[3:]
    rot_mat, _ = cv2.Rodrigues(rot_vec)
    transform_mat = np.concatenate((rot_mat, np.reshape(t_vec, (3, 1))), axis=1)
    points_2d_proj_2 = np.dot(A, np.dot(transform_mat, homo(points_3d).T) ** 2).T
    points_2d_2 = points_2d ** 2
    error = np.linalg.norm(points_2d_proj_2 - points_2d_2, axis=1)

    return np.sum(error)


def tvec2tmat(tvec, pad=False):
    rot_vec = tvec[:3]
    t_vec = tvec[3:]
    rot_mat, _ = cv2.Rodrigues(rot_vec)
    tmat = np.concatenate((rot_mat, np.reshape(t_vec, (3, 1))), axis=1)

    if pad:
        pad_line = np.array([0, 0, 0, 1])
        pad_line = np.reshape(pad_line, (1, 4))
        tmat = np.concatenate((tmat, pad_line))

    return tmat


def main(filenames, pattern_size, square_size):

    n_cams = len(filenames)

    w, h, K, D = load_calib('ost.yaml')
    A = np.array([[1, 0, 0], [0, 1, 1]])

    points_3d = generate_points_3d(pattern_size, square_size)

    n_points = pattern_size[0] * pattern_size[1]

    # points_2d_cam = load_cam_dets_all(filenames=filenames, n_points=n_points)
    # points_2d_radar = load_radar_dets_all(filenames=filenames, n_points=n_points)

    for cam_id in range(n_cams):
        filename = filenames[cam_id]
        fname_cam = os.path.join(filename, filename.split('/')[-1]+'.csv')
        points_2d_cam = load_reflector_dets_csv(fname_cam, n_points=n_points)
        fname_radar = os.path.join(filename, 'radar_dets.txt')
        points_2d_radar = load_radar_dets_txt(fname_radar, n_points=n_points)

        retval, rvec, tvec = cv2.solvePnP(points_3d, points_2d_cam, K, distCoeffs=None)
        rt0 = np.concatenate((rvec, tvec), axis=0)
        rt0 = np.squeeze(rt0)
        opt_res_cam = least_squares(reproj_error, rt0, args=(K, points_2d_cam, points_3d), verbose=1)
        rt_cam_final = opt_res_cam.x

        opt_res_radar = least_squares(reproj_error_radar, rt_cam_final, args=(A, points_2d_radar, points_3d), verbose=1)
        rt_radar_final = opt_res_radar.x

        rt_cam_final_mat = tvec2tmat(rt_cam_final, pad=True)
        rt_radar_final_mat = tvec2tmat(rt_radar_final, pad=True)

        T_cam_radar = np.dot(rt_cam_final_mat, np.linalg.inv(rt_radar_final_mat))

        print(T_cam_radar)

    return


if __name__ == '__main__':

    # csv_dir = "/mnt/disk2/CR_dataset/2019_05_24/2019_05_24_cali002/2019_05_24_cali002.csv"
    # load_reflector_dets_csv(csv_dir, n_points=4)

    main(filenames=FULL_PATHs, pattern_size=(2, 2), square_size=2)

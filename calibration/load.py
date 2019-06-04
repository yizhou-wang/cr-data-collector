import os
import numpy as np
import csv
import json
import yaml
import math

from utils import ra2xy


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

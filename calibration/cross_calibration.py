import os
import numpy as np
import cv2

from scipy.optimize import least_squares

from load import load_calib
from load import load_reflector_dets_csv
from load import load_radar_dets_txt
from load import load_cam_dets_all, load_radar_dets_all
from utils import homo
from utils import rtvec2rtmat

DATA_DIR = "/mnt/disk2/CR_dataset"
DATE = "2019_05_24"
SEQs = ["2019_05_24_cali002", "2019_05_24_cali003"]
FULL_PATHs = [os.path.join(DATA_DIR, DATE, seq) for seq in SEQs]


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


def reproj_error(rt_vec, K, points_2d, points_3d):

    transform_mat = rtvec2rtmat(rt_vec)
    P = np.dot(K, transform_mat)
    points_2d_proj = np.dot(P, homo(points_3d).T).T
    down = np.tile(points_2d_proj[:, -1:], (1, 3))
    points_2d_proj = points_2d_proj / down
    error = np.linalg.norm(points_2d_proj[:, :2] - points_2d, axis=1)

    return np.sum(error)


def reproj_error_radar(rt_vec, A, points_2d, points_3d):

    transform_mat = rtvec2rtmat(rt_vec)
    points_2d_proj_2 = np.dot(A, np.dot(transform_mat, homo(points_3d).T) ** 2).T
    points_2d_2 = points_2d ** 2
    error = np.linalg.norm(points_2d_proj_2 - points_2d_2, axis=1)

    return np.sum(error)


def init_rts(points_2d_cam, points_3d, K):

    # r_radar_cam0 = np.eye(3)
    # t_radar_cam0 = np.array([-0.02, 0.01, -0.01])
    # r_radar_cam_vec0, _ = cv2.Rodrigues(r_radar_cam0)
    # r_radar_cam_vec0 = np.squeeze(r_radar_cam_vec0)
    # rt_radar_cam0 = np.concatenate((r_radar_cam_vec0, t_radar_cam0), axis=0)
    rt_radar_cam0 = np.array([0.01, 0.01, 0.01, -0.02, 0.01, -0.01])

    n_obs = points_2d_cam.shape[0]
    rts0 = rt_radar_cam0
    for obs_id in range(n_obs):
        retval, rvec, tvec = cv2.solvePnP(points_3d, points_2d_cam[obs_id], K, distCoeffs=None)
        rt0 = np.concatenate((rvec, tvec), axis=0)
        rt0 = np.squeeze(rt0)
        rts0 = np.concatenate((rts0, rt0), axis=0)
    return rts0


def cost_joint(rts, n_cams, K, A, points_2d_cam, points_2d_radar, points_3d):
    rt_radar_cam = rts[:6]
    rt_cams = rts[6:]
    rt_cams = np.reshape(rt_cams, (n_cams, 6))
    error_sum = 0

    for cam_id in range(n_cams):
        rt_cam_mat = rtvec2rtmat(rt_cams[cam_id])
        rt_cam_mat_pad = rtvec2rtmat(rt_cams[cam_id], pad=True)
        P = np.dot(K, rt_cam_mat)
        points_2d_proj = np.dot(P, homo(points_3d).T).T
        down = np.tile(points_2d_proj[:, -1:], (1, 3))
        points_2d_proj = points_2d_proj / down
        error = np.linalg.norm(points_2d_proj[:, :2] - points_2d_cam[cam_id], axis=1)
        # print(cam_id, np.sum(error))
        error_sum += np.sum(error)

        rt_radar_cam_mat = rtvec2rtmat(rt_radar_cam)
        rt_radar_mat = np.dot(rt_radar_cam_mat, rt_cam_mat_pad)
        points_2d_proj_2 = np.dot(A, np.dot(rt_radar_mat, homo(points_3d).T) ** 2).T
        points_2d_2 = points_2d_radar[cam_id] ** 2
        error = np.linalg.norm(points_2d_proj_2 - points_2d_2, axis=1)
        # print(cam_id, np.sum(error))
        error_sum += np.sum(error)

    return error_sum


def main(filenames, pattern_size, square_size, method):

    n_cams = len(filenames)

    w, h, K, D = load_calib('ost.yaml')
    A = np.array([[1, 0, 0], [0, 1, 1]])

    points_3d = generate_points_3d(pattern_size, square_size)

    n_points = pattern_size[0] * pattern_size[1]

    if method == 'sep':
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

            rt_cam_final_mat = rtvec2rtmat(rt_cam_final, pad=True)
            rt_radar_final_mat = rtvec2rtmat(rt_radar_final, pad=True)

            # T_cam_radar = np.dot(rt_cam_final_mat, np.linalg.inv(rt_radar_final_mat))
            T_radar_cam = np.dot(rt_radar_final_mat, np.linalg.inv(rt_cam_final_mat))

            print(T_radar_cam)

    if method == 'joint':

        points_2d_cam = load_cam_dets_all(filenames=filenames, n_points=n_points)
        points_2d_radar = load_radar_dets_all(filenames=filenames, n_points=n_points)

        points_2d_cam = np.reshape(points_2d_cam, (n_cams, n_points, -1))
        points_2d_radar = np.reshape(points_2d_radar, (n_cams, n_points, -1))

        rts_0 = init_rts(points_2d_cam, points_3d, K)

        opt_res = least_squares(cost_joint, rts_0, args=(n_cams, K, A, points_2d_cam, points_2d_radar, points_3d), verbose=2)

        rts_final = opt_res.x
        rt_radar_cam_final = rts_final[:6]
        rt_radar_cam_final_mat = rtvec2rtmat(rt_radar_cam_final)
        print(rt_radar_cam_final_mat)

    return


if __name__ == '__main__':

    # csv_dir = "/mnt/disk2/CR_dataset/2019_05_24/2019_05_24_cali002/2019_05_24_cali002.csv"
    # load_reflector_dets_csv(csv_dir, n_points=4)

    main(filenames=FULL_PATHs, pattern_size=(2, 2), square_size=2, method='joint')

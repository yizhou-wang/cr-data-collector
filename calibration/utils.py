import numpy as np
import cv2


def ra2xy(r, a):
    x = r * np.sin(a)
    y = r * np.cos(a)
    return x, y


def homo(points_3d):
    if points_3d.shape[1] < 3 or points_3d.shape[1] > 4:
        raise
    if points_3d.shape[1] == 4:
        return points_3d

    n_points = points_3d.shape[0]
    pad = np.ones((n_points, 1))
    points_3d_homo = np.concatenate((points_3d, pad), axis=1)
    return points_3d_homo


def rtvec2rtmat(trvec, pad=False):
    rot_vec = trvec[:3]
    t_vec = trvec[3:]
    rot_mat, _ = cv2.Rodrigues(rot_vec)
    trmat = np.concatenate((rot_mat, np.reshape(t_vec, (3, 1))), axis=1)

    if pad:
        pad_line = np.array([0, 0, 0, 1])
        pad_line = np.reshape(pad_line, (1, 4))
        trmat = np.concatenate((trmat, pad_line))

    return trmat

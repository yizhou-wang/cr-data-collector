from .cam_driver import run_single_camera
from .cam_mul_driver import run_multiple_cameras
from .radar_driver import copy_radar_data
from .radar_driver import run_radar
from .radar_driver import init_radar
from .radar_driver import check_datetime


def sort_cams(cam_list):
    cam_list = sorted(cam_list, key=lambda x: x.GetUniqueID())
    return cam_list
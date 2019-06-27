import PySpin
import os
import shutil
import time
import datetime
from argparse import ArgumentParser

from collector import run_single_camera
from collector import copy_radar_data


def main(base_dir, seq_name, frame_rate, num_img):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True
    seq_dir = os.path.join(base_dir, seq_name)

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam, seq_dir, frame_rate, num_img)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    print('Done! Copy radar data...')

    # move radar data files to right place
    time.sleep(1)
    copy_radar_data(base_dir, seq_name)

    return result


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-b', '--basedir', dest='base_dir', help='set base directory')
    parser.add_argument('-s', '--seqnum', dest='sequence_number', help='set sequence series name')
    parser.add_argument('-fr', '--framerate', dest='frame_rate', help='set acquisition framerate')
    parser.add_argument('-n', '--numimg', dest='number_of_images', help='set acquisition image number')
    args = parser.parse_args()

    now = datetime.datetime.now()
    cur_date = "%s_%02d_%02d" % (now.year, now.month, now.day)

    MAX_TRY = 3

    try_remain = 1
    while args.base_dir is None or args.base_dir == '':
        if try_remain == 0:
            # args.base_dir = os.path.dirname(os.path.realpath(__file__))
            args.base_dir = 'D:\\RawData'
            break
        else:
            args.base_dir = input("Enter base directory (default='D:\\RawData'): ")
            try_remain -= 1
    args.base_dir = os.path.join(args.base_dir, cur_date)

    try_remain = MAX_TRY
    while args.sequence_number is None or args.sequence_number == '':
        if try_remain == 0:
            raise ValueError('Do not receive sequence name. Quit.')
        args.sequence_number = input("Enter sequence name: ")
        try_remain -= 1
    args.sequence_number = cur_date + '_' + args.sequence_number

    try_remain = 1
    while args.frame_rate is None or args.frame_rate == '':
        if try_remain == 0:
            args.frame_rate = 30
            break
        else:
            args.frame_rate = input("Enter frame rate (default=30): ")
            try_remain -= 1
    try_remain = 1
    while args.number_of_images is None or args.number_of_images == '':
        if try_remain == 0:
            args.number_of_images = 30
            break
        else:
            args.number_of_images = input("Enter number of images (default=30): ")
            try_remain -= 1

    print('Input configurations:')
    print('\tBase Directory:\t', args.base_dir)
    print('\tSequence Name:\t', args.sequence_number)
    print('\tFramerate:\t', args.frame_rate)
    print('\tImage Number:\t', args.number_of_images)
    print('')

    check_config = input("Are the above configurations correct? (y/n) ")
    if check_config is not 'y': 
        print('Wrong configuration. Quit...')
        quit()

    data_dir = os.path.join(args.base_dir, args.sequence_number)
    print(data_dir)
    if os.path.exists(data_dir):
        overwrite = input("Sequence name already exist! Overwrite? (y/n) ")
        if overwrite is not 'y':
            print('Do not overwrite. Quit...')
            quit()
        else:
            shutil.rmtree(data_dir)

    time.sleep(.0000000001)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(os.path.join(data_dir, 'images')):
        os.makedirs(os.path.join(data_dir, 'images'))
    if not os.path.exists(os.path.join(data_dir, 'radar')):
        os.makedirs(os.path.join(data_dir, 'radar'))

    main(args.base_dir, args.sequence_number, float(args.frame_rate), int(float(args.number_of_images)))

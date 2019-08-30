import PySpin
import os
import shutil
import time
import datetime
from argparse import ArgumentParser

from collector import run_single_camera, run_multiple_cameras
from collector import copy_radar_data


def main(base_dir, seq_name, frame_rate, num_img, syn=False):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True
    vertical = False

    seq_dir = os.path.join(base_dir, seq_name)

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

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

    if syn or num_cameras == 1:
        # Run example on each camera
        for i, cam in enumerate(cam_list):
            if not os.path.exists(os.path.join(seq_dir, 'images_%d' % i)):
                os.makedirs(os.path.join(seq_dir, 'images_%d' % i))
                
        if not os.path.exists(os.path.join(seq_dir, 'radar_h')):
            os.makedirs(os.path.join(seq_dir, 'radar_h'))

            print('Running example for camera %d...' % i)

            result &= run_single_camera(cam, seq_dir, frame_rate, num_img)
            print('Camera %d example complete... \n' % i)

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam

    else:

        for i in range(num_cameras):
            if not os.path.exists(os.path.join(seq_dir, 'images_%d' % i)):
                os.makedirs(os.path.join(seq_dir, 'images_%d' % i))

        if not os.path.exists(os.path.join(seq_dir, 'radar_h')):
            os.makedirs(os.path.join(seq_dir, 'radar_h'))

        # Run example on all cameras
        print('Running example for all cameras...')

        result = run_multiple_cameras(cam_list, seq_dir, frame_rate, num_img, radar=True)

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    print('Done! Copy radar data...')

    # move radar data files to right place
    time.sleep(1)
    copy_radar_data(base_dir, seq_name, vertical)

    return result


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-b', '--basedir', dest='base_dir', help='set base directory')
    parser.add_argument('-s', '--seqname', dest='sequence_name', help='set sequence series name')
    parser.add_argument('-fr', '--framerate', dest='frame_rate', help='set acquisition framerate')
    parser.add_argument('-n', '--numimg', dest='number_of_images', help='set acquisition image number')
    parser.add_argument('-ns', '--numseq', dest='number_of_seqs', help='set acquisition sequence number')
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

    try_remain = 1
    while args.number_of_seqs is None or args.number_of_seqs == '':
        if try_remain == 0:
            args.number_of_seqs = 1
            break
        else:
            args.number_of_seqs = input("Enter sequence number (default=1): ")
            try_remain -= 1

    if int(float(args.number_of_seqs)) == 1:
        try_remain = MAX_TRY
        while args.sequence_name is None or args.sequence_name == '':
            if try_remain == 0:
                raise ValueError('Do not receive sequence name. Quit.')
            args.sequence_name = input("Enter sequence name: ")
            try_remain -= 1
        args.sequence_name = [cur_date + '_' + args.sequence_name]
    else:
        n_seq = int(float(args.number_of_seqs))
        n_exist = len(sorted(os.listdir(args.base_dir)))
        indices = range(n_exist, n_exist + n_seq)
        args.sequence_name = [cur_date + '_' + 'onrd' + '%03d' % idx for idx in indices]

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
    print('\tBase Directory:\t\t', args.base_dir)
    print('\tSequence Number:\t', args.number_of_seqs)
    print('\tSequence Name:\t\t', args.sequence_name)
    print('\tFramerate:\t\t', args.frame_rate)
    print('\tImage Number:\t\t', args.number_of_images)
    print('')

    check_config = input("Are the above configurations correct? (y/n) ")
    if check_config is not 'y': 
        print('Wrong configuration. Quit...')
        quit()

    # check sequence name exist
    for name in args.sequence_name:
        data_dir = os.path.join(args.base_dir, name)
        if os.path.exists(data_dir):
            print(name)
            overwrite = input("Sequence name already exist! Overwrite? (y/n) ")
            if overwrite is not 'y':
                print('Do not overwrite. Quit...')
                quit()
            else:
                shutil.rmtree(data_dir)
                time.sleep(.00001)
                os.makedirs(data_dir)
        else:
            os.makedirs(data_dir)

    # for name in args.sequence_name:
    #     data_dir = os.path.join(args.base_dir, name)

    #     if not os.path.exists(os.path.join(data_dir, 'images')):
    #         os.makedirs(os.path.join(data_dir, 'images'))
    #     if not os.path.exists(os.path.join(data_dir, 'radar_h')):
    #         os.makedirs(os.path.join(data_dir, 'radar_h'))

        main(args.base_dir, name, float(args.frame_rate), int(float(args.number_of_images)))

        print('Waiting for data processing ...')
        time.sleep(1)

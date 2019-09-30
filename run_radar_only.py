import os
import shutil
import time
import datetime
from argparse import ArgumentParser
from collector import copy_radar_data
from collector import run_radar
from collector import init_radar
from collector import check_datetime


def run_single_radar(seq_dir, radar=True, interval=0):
    """
    This function is to run the other radar on different laptop
    with interval checking and copy raw radar data
    """
    result = True

    if radar:
        # Init radar
        engine = init_radar()
    
    if radar and interval:
        assert check_datetime(interval) is True
    
    if radar:
        # Run radar
        run_radar(engine)
        result &= True

    # record start time
    start_time = time.time()
    print('Acquiring radar data...')

    with open(os.path.join(seq_dir, 'start_time_v.txt'), 'w') as start_time_txt:
        time_str = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')
        start_time_txt.write("%s\n" % time_str)
        # start_time_txt.write("%s" % start_time)

    return result


def main(base_dir, seq_name, frame_rate, num_img, syn=True, interval=0):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True
    vertical = True
    seq_dir = os.path.join(base_dir, seq_name)

    if not os.path.exists(os.path.join(seq_dir, 'radar_v')):
        os.makedirs(os.path.join(seq_dir, 'radar_v'))

    result &= run_single_radar(seq_dir, interval=interval)
    print('Radar %d example complete... \n' % 1)
   
    # move radar data files to right place
    time.sleep(60)
    copy_radar_data(base_dir, seq_name, vertical)
    print('Done! Copy radar data...')

    return result


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-b', '--basedir', dest='base_dir', help='set base directory')
    parser.add_argument('-s', '--seqname', dest='sequence_name', help='set sequence series name')
    parser.add_argument('-fr', '--framerate', dest='frame_rate', help='set acquisition framerate')
    parser.add_argument('-n', '--numimg', dest='number_of_images', help='set acquisition image number')
    parser.add_argument('-ns', '--numseq', dest='number_of_seqs', help='set acquisition sequence number')
    parser.add_argument('-i', '--interval', dest='interval', help='set time interval')
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

    if not os.path.exists(args.base_dir):
        os.makedirs(args.base_dir)

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

    try_remain = 1
    while args.interval is None or args.interval == '':
        if try_remain == 0:
            args.interval = 3
            break
        else:
            args.interval = input("Enter interval (default=3): ")
            try_remain -= 1

    print('Input configurations:')
    print('\tBase Directory:\t\t', args.base_dir)
    print('\tSequence Number:\t', args.number_of_seqs)
    print('\tSequence Name:\t\t', args.sequence_name)
    print('\tFramerate:\t\t', args.frame_rate)
    print('\tImage Number:\t\t', args.number_of_images)
    print('\tInterval:\t\t', args.interval)
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
        else:
            pass

    for name in args.sequence_name:
        data_dir = os.path.join(args.base_dir, name)
        os.makedirs(data_dir)

        # if not os.path.exists(os.path.join(data_dir, 'radar_v')):
        #     os.makedirs(os.path.join(data_dir, 'radar_v'))

        main(args.base_dir, name, float(args.frame_rate), int(float(args.number_of_images)), interval=int(float(args.interval)))

        print('Waiting for data processing ...')
        time.sleep(1)

import os
import sys
import argparse
import shutil
import time

rename_dict = {
    'images_0': 'images_raw_0',
    'images_1': 'images_raw_1',
}


def parse_args():
    parser = argparse.ArgumentParser(description='Rename some folders in UWCR dataset')
    parser.add_argument('--src_root', type=str, help='source data root directory')
    parser.add_argument('--dates', type=str, help='process dates (separate by comma)')
    parser.add_argument('--names', type=str, default='', help='names of files/folders to copy (separate by comma)')
    parser.add_argument('--names_new', type=str, default='', help='new names of files/folders to copy (separate by comma)')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    """
    Example:
        python rename_data.py --src_root /mnt/nas_crdataset --dates 2019_10_13 \
            --names start_time.txt --names_new start_time_h.txt
    """
    args = parse_args()
    src_root = args.src_root
    dates = args.dates.split(',')
    if args.names == '':  # copy all files/folders
        names = None
    else:
        names = args.names.split(',')
    if args.names_new == '':  # copy all files/folders
        names_new = None
    else:
        names_new = args.names_new.split(',')
    if names is not None and names_new is not None:
        assert len(names) == len(names_new)
    print(names)
    print(names_new)

    for date in dates:
        seqs = sorted(os.listdir(os.path.join(src_root, date)))
        for seq in seqs:
            src_dir = os.path.join(src_root, date, seq)
            if names is None:
                names = os.listdir(src_dir)
            for name_id, name in enumerate(names):
                print("Renaming %s: %s ..." % (src_dir, name))
                if names_new is not None:
                    name_new = names_new[name_id]
                elif name in rename_dict:
                    name_new = rename_dict[name]
                else:
                    raise TypeError
                path_old = os.path.join(src_dir, name)
                path_new = os.path.join(src_dir, name_new)
                if not os.path.exists(path_old):
                    print("Warning: %s does not exist" % path_old)
                    continue
                os.rename(path_old, path_new)

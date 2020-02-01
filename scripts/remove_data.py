import os
import sys
import argparse
import shutil
import time


def parse_args():
    parser = argparse.ArgumentParser(description='Remove some folders/files in UWCR dataset')
    parser.add_argument('--src_root', type=str, help='source data root directory')
    parser.add_argument('--dates', type=str, help='process dates (separate by comma)')
    parser.add_argument('--names', type=str, help='names of files/folders to copy (separate by comma)')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    src_root = args.src_root
    dates = args.dates.split(',')
    names = args.names.split(',')

    for date in dates:
        seqs = sorted(os.listdir(os.path.join(src_root, date)))
        for seq in seqs:
            src_dir = os.path.join(src_root, date, seq)
            if names is None:
                names = os.listdir(src_dir)
            for name in names:
                print("Removing %s: %s ..." % (src_dir, name))
                src_path = os.path.join(src_dir, name)
                if not os.path.exists(src_path):
                    print("Warning: %s does not exist" % src_path)
                    continue
                if os.path.isdir(src_path):
                    shutil.rmtree(src_path)
                else:
                    os.remove(src_path)

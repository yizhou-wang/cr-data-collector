import os
import sys
import argparse
import shutil
import time

rename_dict = {}


def parse_args():
    parser = argparse.ArgumentParser(description='Copy some folders in UWCR dataset')
    parser.add_argument('--src_root', type=str, help='source data root directory')
    parser.add_argument('--dst_root', type=str, help='destination data root directory')
    parser.add_argument('--dates', type=str, help='process dates (separate by comma)')
    parser.add_argument('--names', type=str, default='', help='names of files/folders to copy (separate by comma)')
    parser.add_argument('--rename', action="store_true", help='whether do rename for the files/folders')
    parser.add_argument('--overwrite', action="store_true", help='whether rewrite if exist')
    args = parser.parse_args()
    return args


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copyfile(s, d)


def copy_file(src_dir, dst_dir, filename, rename=False, overwrite=False):
    try:
        src_path = os.path.join(src_dir, filename)
        if rename and filename in rename_dict:
            filerename = rename_dict[filename]
        else:  # if filename not in rename_dict, do not rename
            filerename = filename
        dst_path = os.path.join(dst_dir, filerename)
        if os.path.exists(dst_path):
            if overwrite:
                os.remove(dst_path)
                shutil.copyfile(src_path, dst_path)
            else:
                return True
        else:  # file not exists, copy
            shutil.copyfile(src_path, dst_path)
        return True

    except Exception as e:
        print(e)
        return False


def copy_folder(src_dir, dst_dir, folder_name, rename=False, overwrite=False):
    try:
        src_path = os.path.join(src_dir, folder_name)
        if rename and folder_name in rename_dict:
            dst_path = os.path.join(dst_dir, rename_dict[folder_name])
        else:
            dst_path = os.path.join(dst_dir, folder_name)
        if os.path.exists(dst_path):
            if overwrite:
                shutil.rmtree(dst_path)
                time.sleep(0.1)
            else:
                return True
        os.makedirs(dst_path)
        copytree(src_path, dst_path)
        return True

    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    args = parse_args()
    src_root = args.src_root
    dst_root = args.dst_root
    dates = args.dates.split(',')
    if args.names == '':  # copy all files/folders
        names = None
    else:
        names = args.names.split(',')
    rename = args.rename
    overwrite = args.overwrite

    for date in dates:
        seqs = sorted(os.listdir(os.path.join(src_root, date)))
        for seq in seqs:
            src_dir = os.path.join(src_root, date, seq)
            dst_dir = os.path.join(dst_root, date, seq)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            if names is None:
                names = os.listdir(src_dir)
            for name in names:
                print("Copying %s to %s: %s ..." % (src_dir, dst_dir, name))
                if os.path.isdir(os.path.join(src_dir, name)):
                    copy_folder(src_dir, dst_dir, name, rename, overwrite)
                else:
                    copy_file(src_dir, dst_dir, name, rename, overwrite)

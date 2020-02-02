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
    parser = argparse.ArgumentParser(description='Copy some folders/files in UWCR dataset')
    parser.add_argument('--src_root', type=str, help='source data root directory')
    parser.add_argument('--dst_root', type=str, help='destination data root directory')
    parser.add_argument('--dates', type=str, help='process dates (separate by comma)')
    parser.add_argument('--names', type=str, default='', help='names of files/folders to copy (separate by comma)')
    parser.add_argument('--rename', action="store_true", help='whether do rename for the files/folders')
    parser.add_argument('--names_new', type=str, default='', help='new names for the files/folders')
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


def copy_file(src_dir, dst_dir, filename, filename_new, overwrite=False):
    try:
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, filename_new)
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


def copy_folder(src_dir, dst_dir, folder_name, folder_name_new, overwrite=False):
    try:
        src_path = os.path.join(src_dir, folder_name)
        dst_path = os.path.join(dst_dir, folder_name_new)
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
    """
    Example:
        python copy_data.py --src_root /mnt/nas_crdataset/ --dst_root /mnt/nas_crdataset2/ --dates 2019_10_13 \
            --names rad_reo_zerf,rad_reo_zerf_v --rename --names_new rad_reo_zerf_h,rad_reo_zerf_v --overwrite
    """
    args = parse_args()
    src_root = args.src_root
    dst_root = args.dst_root
    dates = args.dates.split(',')
    if args.names == '':  # copy all files/folders
        names = None
    else:
        names = args.names.split(',')
    rename = args.rename
    if args.names_new == '':  # copy all files/folders
        names_new = None
    else:
        names_new = args.names_new.split(',')
    if names is not None and names_new is not None:
        assert len(names) == len(names_new)
    print(names)
    print(names_new)
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
            for name_id, name in enumerate(names):
                print("Copying %s to %s: %s ..." % (src_dir, dst_dir, name))
                src_path = os.path.join(src_dir, name)
                if not os.path.exists(src_path):
                    print("Warning: %s does not exist" % src_path)
                    continue
                if rename:
                    if names_new is not None:
                        name_new = names_new[name_id]
                    elif name in rename_dict:
                        name_new = rename_dict[name]
                    else:
                        raise TypeError
                else:
                    name_new = name
                if os.path.isdir(src_path):
                    copy_folder(src_dir, dst_dir, name, name_new, overwrite)
                else:
                    copy_file(src_dir, dst_dir, name, name_new, overwrite)

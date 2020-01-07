import os, sys
import shutil
import time

sys.path.append(os.path.abspath('..'))
from utils.dataset_tools import fix_cam_drop_frames, calculate_frame_offset

rename_dict = {
    'images': 'images_raw_0',
    'images_0': 'images_raw_0',
    'images_1': 'images_raw_1',
    'images_udst': 'images_0',
    'images_hist_0': 'images_0',
    'images_hist_1': 'images_1',
    'radar_chirps_win_RISEP': 'radar_chirps_win_RISEP_h',
    'start_time.txt': 'start_time_h.txt',
    'start_time_v.txt': 'start_time_v.txt',
    'timestamps.txt': 'timestamps_0.txt',
    'timestamps_0.txt': 'timestamps_0.txt',
    'timestamps_1.txt': 'timestamps_1.txt',
    'mask_obj_img': 'masks_obj_viz',
    'depth_mono': 'depth_mono',
}


def copy_images(old_folder_name, startid, nframes, overwrite=False, ext='jpg'):
    try:
        src_path = os.path.join(path_old, old_folder_name)
        img_names = sorted(os.listdir(src_path))
        img_names = fix_cam_drop_frames(path_old, img_names)
        try:
            dst_path = os.path.join(path_new, rename_dict[old_folder_name])
        except:
            dst_path = os.path.join(path_new, old_folder_name)
        if os.path.exists(dst_path):
            if overwrite:
                shutil.rmtree(dst_path)
                time.sleep(0.1)
            else:
                print("Skip ...")
                return True
        print("... %s ..." % old_folder_name)
        os.makedirs(dst_path)
        for idx, img_name in enumerate(img_names[startid:startid+nframes]):
            src_im = os.path.join(src_path, img_name)
            dst_im = os.path.join(dst_path, "%010d." % idx + ext)
            shutil.copyfile(src_im, dst_im)
        return True

    except Exception as e:
        print(e)
        return False


def copy_radar_npy(old_folder_name, startid, nframes, chirpids, overwrite=False):
    print("... %s ..." % old_folder_name)
    try:
        src_path = os.path.join(path_old, old_folder_name)
        chirp_names = sorted(os.listdir(src_path))
        dst_path = os.path.join(path_new, rename_dict[old_folder_name])
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for chirp_name in chirp_names:
            if int(chirp_name) not in chirpids:
                continue
            if os.path.exists(os.path.join(dst_path, chirp_name)):
                if overwrite:
                    shutil.rmtree(os.path.join(dst_path, chirp_name))
                    time.sleep(0.1)
                else:
                    print("Skip ...")
                    continue
            frame_names = sorted(os.listdir(os.path.join(src_path, chirp_name)))
            for idx, rad_name in enumerate(frame_names[startid:startid+nframes]):
                src_rad = os.path.join(src_path, chirp_name, rad_name)
                dst_rad = os.path.join(dst_path, chirp_name, "%06d.npy" % idx)
                if not os.path.exists(os.path.join(dst_path, chirp_name)):
                    os.makedirs(os.path.join(dst_path, chirp_name))
                shutil.copyfile(src_rad, dst_rad)
        return True

    except Exception as e:
        print(e)
        return False


def copy_file(filename):
    try:
        print("... %s ..." % filename)
        src_ts = os.path.join(path_old, filename)
        try:
            filerename = rename_dict[filename]
        except:
            filerename = filename
        dst_ts = os.path.join(path_new, filerename)
        if os.path.exists(dst_ts):
            os.remove(dst_ts)
        shutil.copyfile(src_ts, dst_ts)
        return True

    except Exception as e:
        print(e)
        return False


def update_timestamps(filename, startid, nframes):
    try:
        print("... %s ..." % filename)
        src_ts = os.path.join(path_old, filename)
        if not os.path.exists(src_ts):
            print("No dst file exists.")
            return False
        try:
            filerename = rename_dict[filename]
        except:
            filerename = filename
        dst_ts = os.path.join(path_new, filerename)
        if os.path.exists(dst_ts):
            os.remove(dst_ts)

        with open(src_ts, 'r') as fsrc:
            data = fsrc.readlines()
        data_new = fix_cam_drop_frames(path_old, data)

        with open(dst_ts, 'w') as fdst:
            for line in data_new[startid:startid+nframes]:
                fdst.write(line)

        return True

    except Exception as e:
        print(e)
        return False


def update_mrcnn_txt(txt_name, startid_cam, nframes):
    txt_path = os.path.join(path_old, txt_name)
    dst_txt_path = os.path.join(path_new, txt_name)
    with open(txt_path, 'r') as fsrc:
        data = fsrc.readlines()
    # data = fix_cam_drop_frames(path_old, data)

    with open(dst_txt_path, 'w') as fdst:
        for line in data:
            line_list = line.rstrip().split(',')
            frameid_old = int(line_list[0])
            if frameid_old < startid_cam or frameid_old >= startid_cam+nframes:
                continue
            else:
                frameid_new = frameid_old - startid_cam
                line_list[0] = str(frameid_new)
                fdst.write(','.join(line_list) + '\n')


def copy_masks(folder_name, startid_cam, nframes, overwrite=False):
    folder_path_old = os.path.join(path_old, folder_name)
    folder_path_new = os.path.join(path_new, folder_name)
    npys = os.listdir(folder_path_old)
    if overwrite:
        if os.path.exists(folder_path_new):
            shutil.rmtree(folder_path_new)
            time.sleep(0.1)
    if not os.path.exists(folder_path_new):
        os.makedirs(folder_path_new)
    for npy in npys:
        frameid_old, objid = npy.split('.')[0].split('_')
        frameid_old = int(frameid_old)
        if frameid_old < startid_cam or frameid_old >= startid_cam+nframes:
            continue
        else:
            frameid_new = frameid_old - startid_cam
            npy_new = "%010d" % frameid_new + '_' + objid + '.pkl'
            src_npy = os.path.join(folder_path_old, npy)
            dst_npy = os.path.join(folder_path_new, npy_new)
            shutil.copyfile(src_npy, dst_npy)


def update_mrcnndets(startid_cam, nframes, overwrite=False):
    update_mrcnn_txt('mrcnn_dets.txt', startid_cam, nframes)
    copy_masks('masks_obj', startid_cam, nframes, overwrite=overwrite)
    copy_images('mask_obj_img', startid_cam, nframes, overwrite=overwrite)


data_root_old = '/mnt/nas_crdataset'
data_root_new = '/mnt/nas_crdataset2'

dates = []
folders = sorted(os.listdir(data_root_old))
for folder in folders:
    if len(folder) == 10 and folder[:3] == '201':
        dates.append(folder)
dates = dates[:-1]
# dates = dates[11:15]
dates = ['2019_09_29']

for date in dates:
    if date == "2019_04_22":
        continue
    seqs = sorted(os.listdir(os.path.join(data_root_old, date)))
    for seq in seqs:
        print(seq)
        if 'onrd' in seq:
            frame_exp = 40
        else:
            frame_exp = 0
        path_old = os.path.join(data_root_old, date, seq)
        path_new = os.path.join(data_root_new, date, seq)
        if not os.path.exists(path_new):
            os.makedirs(path_new)
        folders = os.listdir(path_old)

        if 'WIN_PROC_MAT_DATA' in folders:
            src_folder_mat = os.path.join(path_old, 'WIN_PROC_MAT_DATA')
            mat_names = sorted(os.listdir(src_folder_mat))
            nrframes = len(mat_names)
            rstartid = int(mat_names[0][:-4].split('_')[-1])
        else:
            print("Warning: %s unfinished!" % seq)
            # nrframes = len(os.path.join(path_old, 'images'))
            # rstartid = 0
            continue

        # if 'radar_chirps_win_RISEP' in folders:
        #     print("... radar_chirps_win_RISEP_h ...")
        #     src_folder_rnpy = os.path.join(path_old, 'radar_chirps_win_RISEP')
        #     dst_folder_rnpy = os.path.join(path_new, 'radar_chirps_win_RISEP_h')
        #     if os.path.exists(dst_folder_rnpy):
        #         shutil.rmtree(dst_folder_rnpy)
        #         time.sleep(0.1)
        #     shutil.copytree(src_folder_rnpy, dst_folder_rnpy)
        # else:
        #     print("Warning: %s unfinished!" % seq)
        #     continue

        start_time_txt = os.path.join(path_old, 'start_time.txt')
        offsetrc, _, _ = calculate_frame_offset(start_time_txt)
        nframes = nrframes - frame_exp - offsetrc
        startid_cam = rstartid + frame_exp
        startid_rad = rstartid + frame_exp + offsetrc

        print("n_frames: %d, start_cam: %d, start_rad: %d" % (nframes, startid_cam, startid_rad))

        # for f in folders:
        #     if f.endswith('.csv'):
        #         copy_file(f)

        # copy_file('timestamps.txt')
        # copy_file('timestamps_0.txt')
        # copy_file('timestamps_1.txt')
        # update_timestamps('timestamps.txt', startid_cam, nframes)
        # update_timestamps('timestamps_0.txt', startid_cam, nframes)
        # update_timestamps('timestamps_1.txt', startid_cam, nframes)
        # copy_file('start_time.txt')
        # copy_file('start_time_v.txt')

        # copy_images('images_udst', startid_cam, nframes)
        # copy_images('images_hist_0', startid_cam, nframes)
        # copy_images('images_hist_1', startid_cam, nframes)
        # copy_images('images', startid_cam, nframes)
        # copy_images('images_0', startid_cam, nframes)
        # copy_images('images_1', startid_cam, nframes)
        # copy_images('masks_seg', startid_cam, nframes, overwrite=True, ext='npy')
        # copy_images('masks_seg_viz', startid_cam, nframes, overwrite=True)
        # copy_images('depth_mono', startid_cam, nframes, ext='npy')

        if 'mrcnn_dets.txt' in folders and 'masks_obj' in folders and 'mask_obj_img' in folders:
            update_mrcnndets(startid_cam, nframes, overwrite=True)
        else:
            print("Files are not complete for updating mrcnn results.")

        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[0, 50, 101, 152, 203, 254])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[1, 51, 102, 153, 204])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[2, 52, 103, 154, 205])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[3, 53, 104, 155, 206])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[4, 54, 105, 156, 207])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[5, 55, 106, 157, 208])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[6, 56, 107, 158, 209])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[7, 57, 108, 159, 210])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[8, 58, 109, 160, 211])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[9, 59, 110, 161, 212])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[10, 60, 111, 162, 213])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[11, 61, 112, 163, 214])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[12, 62, 113, 164, 215])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[13, 63, 114, 165, 216])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[14, 64, 115, 166, 217])

        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[15, 65, 116, 167, 218])
        # copy_radar_npy('radar_chirps_win_RISEP', startid_rad-rstartid, nframes, chirpids=[16, 66, 117, 168, 219])


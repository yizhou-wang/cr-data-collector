import os
import shutil
import time
from pymouse import PyMouse
from pykeyboard import PyKeyboard


def run_radar():
    radar_m = PyMouse()
    radar_k = PyKeyboard()
    x_dim, y_dim = radar_m.screen_size()

    # click DCA1000RAM
    radar_m.click(x_dim // 2 - 150, y_dim // 2 - 120, 1)
    time.sleep(0.5)
    ## record the click time and click trigger
    radar_m.click(x_dim // 2 - 70, y_dim // 2 - 100, 1)

    print("Radar started.")

    return


def copy_radar_data(base_dir, seq_name):
    radar_root = "C:\\ti\\mmwave_studio_01_00_00_00\\mmWaveStudio\\PostProc"
    original_files = sorted(os.listdir(os.path.join(radar_root)))
    TIME_FLAG = 0
    n_files = 0
    size_min = 1000
    for fname in original_files:
        if fname.startswith("adc_data_Raw_") and fname.endswith(".bin"):
            old_path = os.path.join(radar_root, fname)
            time_new = os.path.getmtime(old_path)
            size_old = os.path.getsize(old_path)
            if size_old > size_min:
                if time_new > TIME_FLAG:
                    TIME_FLAG = time_new
                    new_path = os.path.join(base_dir, seq_name, 'radar', fname)
                    shutil.copyfile(old_path, new_path)
                    n_files += 1
            else:
                print("Error!!! The size of data file is less than 1000kB, possiblely there is no radar data!!")
                print("Please recapture this sequence and overwrite it")
                break

    time_cur = time.time()
    if time_cur - time_new > 300:
        print("WARNING!!! May copied old data, please check")

    print("Copied %d radar data files to right place." % n_files)
    return

import os
import shutil
import time
import matlab.engine
import datetime
# from pymouse import PyMouse
# from pykeyboard import PyKeyboard


def check_datetime(interval):
    """
    This function checks the current compter time and if it is 
    the integer multiples of desired interval, return True
    """ 

    while True:
        cur_datetime_min = datetime.datetime.now().minute 
        cur_datetime_sec = datetime.datetime.now().second  
        if cur_datetime_min % interval == 0 and cur_datetime_sec == 0:
            return True


def init_radar():
    """
    This function init the radar function, includes init demo etc
    return the matlab engine
    """
    eng = matlab.engine.start_matlab()
    print('start matlab engine')
    # add search path
    eng.addpath('D:\\Documents\\GitHub\\cr-data-collector\\archive')
    
    return eng


def run_radar(eng):
    """
    This function start radar frame by use matlab command to
    communicate with mmwavestudio software
    Previously, we use virtual interface to control the mouse 
    """
    # previous method
    # radar_m = PyMouse()
    # radar_k = PyKeyboard()
    # x_dim, y_dim = radar_m.screen_size()
    #
    # # click DCA1000RAM
    # radar_m.click(x_dim // 2 - 150, y_dim // 2 - 120, 1)
    # time.sleep(0.5)
    #
    # # record the click time and click trigger
    # radar_m.click(x_dim // 2 - 70, y_dim // 2 - 100, 1)

    cur_datetime = datetime.datetime.now().second
    # matlab control method
    # Init radar
    eng.Init_DataCaptureDemo(nargout=0)
    print('Radar Initialization finished. Prepared to record data...')
    # avoid the two operation too close (result in data lack)
    # time.sleep(1)
    
    while True:
       new_datetime = datetime.datetime.now().second
       if new_datetime == cur_datetime + 5:
            break

    eng.start_frame(nargout=0)
    print("Radar started.")
    # time.sleep(40)
    eng.quit()
    print('Stop matlab engine')

    return


def copy_radar_data(base_dir, seq_name):
    """
    This function is to copy the raw radar file after the capturation
    """
    radar_root = "C:\\ti\\mmwave_studio_02_00_00_02\\mmWaveStudio\\PostProc"
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
                print("Error!!! The size of data file is less than 1000kB, \
                    possiblely there is no radar data!!")
                print("Please recapture this sequence and overwrite it")
                break

    time_cur = time.time()
    if time_cur - time_new > 300:
        print("WARNING!!! May copied old data, please check")

    print("Copied %d radar data files to right place." % n_files)
    return


if __name__ == '__main__':

    # testing
    engine = init_radar()
    run_radar(engine)


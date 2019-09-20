import os
import datetime

store_dir = 'Z:\\'

def Packet_reorder_zerofill(file_dir, file_out_name, file_name):

    log_dir = 'D:\\tmp\\radar_pp\\' + file_name
    if os.path.exists(log_dir) is False:
        os.makedirs(log_dir)

    command = 'C:\\ti\\mmwave_studio_02_00_00_02\\mmWaveStudio\\PostProc\\Packet_Reorder_Zerofill.exe ' \
                + file_dir + ' ' + file_out_name + ' ' + log_dir + '\\log.txt'
    os.system(command)
    
def reorder_zerofill_for_seq(folder_dir, seq):

    file_names = sorted(os.listdir(folder_dir))
    folder_out_dir = folder_dir.replace('radar', 'rad_reo_zerf')

    if not os.path.exists(folder_out_dir):
        os.makedirs(folder_out_dir)
    
    for file_name in file_names:
        index = file_name[-5];
        file_dir = os.path.join(folder_dir, file_name)
        file_out_name = os.path.join(folder_out_dir, 'adc_data_' + index + '.bin')
        file_reo_zef = Packet_reorder_zerofill(file_dir, file_out_name, seq)

def reorder_zerofill_for_date(date, data_dir=store_dir):

    base_dir = os.path.join(data_dir, date)

    if not os.path.exists(base_dir):
        raise ValueError("Data not found!")

    seqs = sorted(os.listdir(base_dir))
    for seq in seqs:
        folder_dir = os.path.join(base_dir, seq, 'radar_')
        print("Packet reorder and zerofill %s ..." % folder_dir)
        try:
            folder_dir_h = folder_dir + 'h'
            reorder_zerofill_for_seq(folder_dir_h,seq)
        except:
            print('donot have the horizontal radar data')
        
        try:
            folder_dir_v = folder_dir + 'v'
            reorder_zerofill_for_seq(folder_dir_v,seq)
        except:
            print('do not have the vertical radar data')

    print("\nPacket reorder and zerofill finished for date %s." % date)


if __name__ == '__main__':

    date = input("Enter date (default=today): ")
    if date == '':
        now = datetime.datetime.now()
        date = "%s_%02d_%02d" % (now.year, now.month, now.day)

    reorder_zerofill_for_date(date)

import numpy as np
import pandas as pd
import os

data_root = '/mnt/nas_crdataset'
# dates = sorted(os.listdir(data_root))
dates = ['2019_04_30', '2019_05_09', '2019_05_23', '2019_05_28', '2019_05_29']


def csv2txt(date, seq_name):

    label_folder = os.path.join(data_root, date, seq_name, 'labels_dets')
    if not os.path.isdir(label_folder):
        os.makedirs(label_folder)

    n_frames = len(os.listdir(os.path.join(data_root, date, seq_name, 'images_udst')))
    label_csv_name = os.path.join(data_root, date, seq_name, 'image_labels.csv')
    data = pd.read_csv(label_csv_name)

    for i in range(n_frames):
        file_idx = format(i, '#010d')
        sub_data = np.asarray(data.loc[data['filename'] == file_idx+".jpg", :])
        txt = []
        for j in range(len(sub_data)):
            row = []
            word = sub_data[j, 6].split(",")
            if len(word) == 1:
                if word[0] == '{}':
                    print(file_idx, 'empty detection:', word)
                    continue
                else:
                    raise ValueError
            row.append(word[0].split(":")[1].lower()[1:-1])         # class_type
            row.append(word[2].split(":")[1][1:-1])                 # truncated
            row.append(word[1].split(":")[1][1:-1])                 # occlusion
            # row.append("-1")                                        # alpha
            row.append(word[3].split(":")[1][1:-2])                 # reachability
            bbox = sub_data[j, 5].split(",")
            row.append(int(bbox[1].split(":")[1]))                   # x
            row.append(int(bbox[2].split(":")[1]))                   # y
            row.append(int(row[4])+int(bbox[3].split(":")[1]))       # x + w
            row.append(int(row[5])+int(bbox[4].split(":")[1][:-1]))  # y + h
            for k in range(7):
                row.append("-1000")                                  # 3d dim & loc
            row.append(1.0)                                          # score
            txt.append(row)
        txt_file = os.path.join(label_folder, file_idx + ".txt")
        np.savetxt(txt_file, txt, delimiter=' ', fmt="%s")


if __name__ == '__main__':

    for date in dates:
        seqs = sorted(os.listdir(os.path.join(data_root, date)))
        for seq in seqs:
            print('Processing %s ...' % seq)
            csv2txt(date, seq)

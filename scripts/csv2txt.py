import numpy as np
import pandas as pd
import os
label_folder = "./labels/"
if not os.path.isdir(label_folder):
    os.makedirs(label_folder)
n_frames = 900
data = pd.read_csv('labels.csv')
for i in range(n_frames):
    file_idx = format(i, '#010d')
    sub_data = np.asarray(data.loc[data['filename'] == file_idx+".jpg", :])
    txt = []
    for j in range(len(sub_data)):
        row = []
        word = sub_data[j,6].split(",")
        row.append(word[0].split(":")[1].lower()[1:-1])         # class_type 
        row.append(word[2].split(":")[1][1:-1])                 # truncated
        row.append(word[1].split(":")[1][1:-1])                 # occlusion
        row.append("-1")                                        # alpha
        bbox = sub_data[j,5].split(",")
        row.append(int(bbox[1].split(":")[1]))                   # x
        row.append(int(bbox[2].split(":")[1]))                   # y
        row.append(int(row[4])+int(bbox[3].split(":")[1]))       # x + w 
        row.append(int(row[5])+int(bbox[4].split(":")[1][:-1]))  # y + h
        for k in range(7):
            row.append("-1000")                                  # 3d dim & loc
        row.append(1.0)                                          # score
        txt.append(row)
    txt_file = label_folder + file_idx + ".txt"
    np.savetxt(txt_file, txt, delimiter=' ',fmt="%s")


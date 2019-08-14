import os
import csv
import math
import json
import numpy as np 
import pandas as pd
n_frames = 900 
labels_path = "./labels/"
images_path = "./images/"
file_attributes = '{"caption":"","public_domain":"no","image_url":""}'
region_shape_attributes = {"name": "rect", "x": 0,"y":0,"width":0,"height":0}
region_attributes = {"class":None,"occlusion":"0","truncation":"0","reachability":"1"}
columns=['filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
       'region_shape_attributes', 'region_attributes']
data = []
for i in range(n_frames):
    sequence = format(i, '#010d')
    img_name = sequence+".jpg"
    label_path = labels_path+sequence+".txt"
    txt_size = os.path.getsize(label_path)
    img_size = os.path.getsize(images_path+img_name)
    if(txt_size>0):
        frame_data = pd.read_csv(label_path,header=None,delimiter='\t').values
        region_count = frame_data.shape[0]
        for obj_id in range(region_count):
            row = []
            array = frame_data[obj_id][0].split()
            row.append(img_name)
            row.append(img_size)
            row.append(file_attributes)
            row.append(region_count)
            row.append(obj_id)
            region_shape_attributes["x"] = array[4]
            region_shape_attributes["y"] = array[5]
            region_shape_attributes["width"] = str(int(array[6])-int(array[4]))
            region_shape_attributes["height"] = str(int(array[7])-int(array[5]))
            row.append(json.dumps(region_shape_attributes))
            region_attributes["class"] = array[0]
            region_attributes["occlusion"] = array[2]
            region_attributes["truncation"] = array[1]
            row.append(json.dumps(region_attributes))
            data.append(row) 
df = pd.DataFrame(data,columns=['filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
       'region_shape_attributes', 'region_attributes'])
df.to_csv(r'labels.csv', index = None, header=True)


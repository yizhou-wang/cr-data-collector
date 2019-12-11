import os
import math
import json
import re
import pandas as pd

from utils import find_nearest
from utils.mappings import labelmap2ra

from config import class_ids, data_sets
from config import t_cl2rh


def correct():
    """
    correct csv that was mistakely converted to csv text format
    """

    label_csv_name = "ramap_labels.csv"
    os.rename(label_csv_name, "ramap_labels_old.csv")
    data = pd.read_csv(label_csv_name)
    n_row, n_col = data.shape

    columns = ['filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
               'region_shape_attributes', 'region_attributes']
    data_update = []

    for r in range(n_row):
        everything = data['filename'][r]
        # everything_list = everything.split(',')
        everything_list = re.split(',(?=(?:[^"]*\"[^"]*\")*[^"]*$)', everything)
        # filename = everything_list[0]
        # file_size = everything_list[1]
        # file_attributes = everything_list[2]
        # region_count = everything_list[3]
        # region_id = everything_list[4]
        # region_shape_attributes = everything_list[5]
        # region_attributes = everything_list[6]
        #
        # row = []
        # row.append(filename)
        # row.append(file_size)
        # row.append(file_attributes)
        # row.append(region_count)
        # row.append(region_id)
        # row.append(region_shape_attributes)
        # row.append(region_attributes)
        data_update.append(everything_list)
    df = pd.DataFrame(data_update, columns=columns)
    df.to_csv("ramap_labels.csv", index=None, header=True)
    print("\tSuccess!")


if __name__ == "__main__":
    correct()

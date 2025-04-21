import numpy as np
import csv
import yaml
import os

from general_functions import load_rotation, rotation_to_inv_matrix


# loads a csv file into a numpy array
def load_csv_file_into_nparray(file_address):
    with open(file_address, 'r') as f:
        return load_csv_into_nparray(f)
    
# loads an iterable of strings in csv format into a numpy array
def load_csv_into_nparray(iterable):
    reader = csv.reader(iterable)
    data = list(reader)
    
    if data[-1] == []:
        # get rid of empty last line if reading an uploaded file
        data = data[:-1]    
    
    return np.array(data, dtype=float)
    
# loads a space separated file into a numpy array
def load_space_separated_into_nparray(file_address):
    data = []
    with open(file_address, 'r') as f:
        for line in f:
            data.append(line.split())
        return np.array(data, dtype=float)

# loads timestamps from file
def load_timestamps_file_into_nparray(file_address):
    with open(file_address, 'r') as f:
        return load_timestamps_into_nparray(f)

# loads timestamps from an iterable of strings in csv format and converts them
# skips first line and then saves only the first column
def load_timestamps_into_nparray(iterable):
    reader = csv.reader(iterable)
    data = list(reader)

    if data[-1] == []:
        # get rid of empty last line if reading an uploaded file
        data = data[:-1]
    
    timestamps_raw = []
    for row in data[1:]:
        timestamps_raw.append(row[0])
    timestamps_nparray = np.array(timestamps_raw, dtype=float)
    # convert timestamps so that they start from 0 and are in seconds
    timestamp0 = int(timestamps_nparray[0])
    return (timestamps_nparray - timestamp0) / 1000000000  # nanoseconds to seconds

# loads a yaml file into a python dictionary
def load_yaml_into_dict(file_address):
    with open(file_address, 'r') as f:
        data = yaml.safe_load(f)
        return data
    
# load a pcl timestamps file (2 columns, space separated, in the second column a timestamp in seconds)
def load_pcl_timestamps(file_address):
    pcl_timestamps = []
    with open(file_address, "r") as f:
        for line in f:
            split_line = line.split()
            if len(split_line) >= 2:
                pcl_timestamps.append(float(split_line[1]))
    return pcl_timestamps

# load predicted translations in distances 25m, 50m, 75m, 100m
def load_gauge_translations(directory_path, filename_prefix):
    translations = []
    for distance in [25, 50, 75, 100]:
        filename = f"{filename_prefix}_{distance}.csv"
        file_path = os.path.join(directory_path, filename)
        translations.append(load_space_separated_into_nparray(file_path)[:, [2, 0, 1]])
    return translations


# load predicted rotations in distances 25m, 50m, 75m, 100m
def load_gauge_rotations(directory_path, filename_prefix):
    gauge_rotations = [[] for _ in range(4)]
    for i in range(4):   # for eveery distance
        filename = f"{filename_prefix}_{25 + i*25}.csv"
        file_path = os.path.join(directory_path, filename)
        gauge_rotations_raw = load_space_separated_into_nparray(file_path)
        for rotation_raw in gauge_rotations_raw:
            rotation = load_rotation(rotation_raw)
            gauge_rotations[i].append(rotation_to_inv_matrix(rotation))
    return gauge_rotations

## @file loading_functions.py
# @author Zuzana Miškaňová
# @brief Contains definitions of functions used for loading various types of data from files.

import numpy as np
import csv
import yaml
import os

from general_functions import load_rotation, rotation_to_inv_matrix


## @brief Loads a csv file into a numpy array.
# @param file_address A path to a csv file.
# @return A numpy array.
def load_csv_file_into_nparray(file_address):
    with open(file_address, 'r') as f:
        return load_csv_into_nparray(f)
    

## @brief Loads an iterable of strings in csv format into a numpy array.
# @param iterable An iterable of strings.
# @return A numpy array.
def load_csv_into_nparray(iterable):
    reader = csv.reader(iterable)
    data = list(reader)
    
    if data[-1] == []:
        # get rid of empty last line if reading an uploaded file
        data = data[:-1]    
    
    return np.array(data, dtype=float)


## @brief Loads a space separated file into a numpy array.
# @param file_address A path to a space separated file.
# @return A numpy array.
def load_space_separated_file_into_nparray(file_address):
    with open(file_address, 'r') as f:
        return load_space_separated_into_nparray(f)
    

## @brief Loads an iterable of strings with space separated values into a numpy array.
# @param iterable An iterable of strings with space separated values.
# @return A numpy array.
def load_space_separated_into_nparray(iterable):
    data = []
    for line in iterable:
        data.append(line.split())
    
    if data[-1] == []:
        # get rid of empty last line if reading an uploaded file
        data = data[:-1]

    return np.array(data, dtype=float)


## @brief Loads timestamps from a file into a numpy array.
# @param file_address A path to a file containing timestamps.
# @return A numpy array.
def load_timestamps_file_into_nparray(file_address):
    with open(file_address, 'r') as f:
        return load_timestamps_into_nparray(f)


## @brief Loads timestamps from an iterable of strings in csv format into a numpy array.
# Skips first line and then saves only the first column.
# Converts the timestamps so that they start from zero.
# @param iterable An iterable of strings with timestamps.
# @return A numpy array.
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


## @brief Loads a yaml file into a python dictionary.
# @param file_address A path to a yaml file.
# @return Data from the file in a Python dictionary.
def load_yaml_into_dict(file_address):
    with open(file_address, 'r') as f:
        data = yaml.safe_load(f)
        return data


## @brief Loads point cloud timestamps from a file into a list.
# @param file_address A path to a file containing point cloud timestamps.
# @return A list containing the timestamps.
def load_pcl_timestamps_file(file_address):
    with open(file_address, "r") as f:
        return load_pcl_timestamps(f)


## @brief Loads point cloud timestamps from an iterable of strings into a list.
# The format: 2 columns, space separated, the timestamp in seconds is in the second column.
# @param iterable An iterable of strings containing point cloud timestamps.
# @return A list containing the timestamps.
def load_pcl_timestamps(iterable):
    pcl_timestamps = []

    for line in iterable:
        split_line = line.split()
        if len(split_line) >= 2:
            pcl_timestamps.append(float(split_line[1]))
    return pcl_timestamps


## @brief Loads predicted train profile translations in distances 25m, 50m, 75m and 100m.
# @param directory_path Path to the directory with the files.
# @param filename_prefix The prefix of the files. Filenames must be: [prefix]_25.csv, etc.
# @return The loaded translations.
def load_profile_translations(directory_path, filename_prefix):
    translations = []
    for distance in [25, 50, 75, 100]:
        filename = f"{filename_prefix}_{distance}.csv"
        file_path = os.path.join(directory_path, filename)
        translations.append(load_space_separated_file_into_nparray(file_path)[:, [2, 0, 1]])
    return translations


## @brief Loads predicted train profile rotations in distances 25m, 50m, 75m and 100m.
# @param directory_path Path to the directory with the files.
# @param filename_prefix The prefix of the files. Filenames must be: [prefix]_25.csv, etc.
# @return The loaded rotations.
def load_profile_rotations(directory_path, filename_prefix):
    rotations = [[] for _ in range(4)]
    for i in range(4):   # for eveery distance
        filename = f"{filename_prefix}_{25 + i*25}.csv"
        file_path = os.path.join(directory_path, filename)
        rotations_raw = load_space_separated_file_into_nparray(file_path)
        for rotation_raw in rotations_raw:
            rotation = load_rotation(rotation_raw)
            rotations[i].append(rotation_to_inv_matrix(rotation))
    return rotations

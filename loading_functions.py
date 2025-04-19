import numpy as np
import csv
import yaml


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

# loads timestamps from file (like csv, but skips first line and saves only the first column)
def load_timestamps_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        
        result = []
        for row in data[1:]:
            result.append(row[0])
        return np.array(result, dtype=float)

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

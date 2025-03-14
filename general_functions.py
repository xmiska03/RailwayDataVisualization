import numpy as np
import csv
import yaml
from params import NEAR_PLANE, FAR_PLANE


# loads a csv file into a numpy array
def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)

# loads a yaml file into a python dictionary
def load_yaml_into_dict(file_address):
    with open(file_address, 'r') as f:
        data = yaml.safe_load(f)
        return data

# creates a deck.gl-style projection matrix according to camera parameters
def calculate_projection_matrix(camera_params_dict):
    w = camera_params_dict['Camera.width']
    h = camera_params_dict['Camera.height']
    f_x = camera_params_dict['CameraMat']['data'][0]
    f_y = camera_params_dict['CameraMat']['data'][4]
    c_x = camera_params_dict['CameraMat']['data'][2]
    c_y = camera_params_dict['CameraMat']['data'][5]
    f = FAR_PLANE
    n = NEAR_PLANE

    proj_mat = np.array([
        [2 * f_x / w,            0,   2 * c_x / w - 1,                    0],
        [          0,  2 * f_y / h,   2 * c_y / h - 1,                    0],
        [          0,            0,  -(f + n)/(f - n), -(2 * f * n)/(f - n)],
        [          0,            0,                -1,                    0] 
    ])
    return proj_mat.transpose().flatten()

# creates transformation matrix from translation and rotation data
def calculate_transformation_matrix(trans, rot_mat_3x3):
    trans_matrix = np.array([
        [1, 0, 0, -trans[2]],
        [0, 1, 0, -trans[0]],
        [0, 0, 1, -trans[1]],
        [0, 0, 0, 1]
    ])
    rot_matrix = np.array([
        [rot_mat_3x3[2][2], rot_mat_3x3[2][0], rot_mat_3x3[2][1], 0],
        [rot_mat_3x3[0][2], rot_mat_3x3[0][0], rot_mat_3x3[0][1], 0],
        [rot_mat_3x3[1][2], rot_mat_3x3[1][0], rot_mat_3x3[1][1], 0],
        [0, 0, 0, 1]
    ])
    return rot_matrix @ trans_matrix

# function used for loading gauge positioning
# it is needed to translate the frame to "trans_point" and then rotate around that point
# that is equivalent to rotating around [0, 0, 0] and then translating to "trans_point"
def calculate_loading_gauge_transformation_matrix(trans_point, rot_mat_3x3):
    trans_matrix = np.array([
        [1, 0, 0, trans_point[2]],
        [0, 1, 0, trans_point[0]],
        [0, 0, 1, trans_point[1]],
        [0, 0, 0, 1]
    ])
    rot_matrix = np.array([
        [rot_mat_3x3[2][2], rot_mat_3x3[2][0], rot_mat_3x3[2][1], 0],
        [rot_mat_3x3[0][2], rot_mat_3x3[0][0], rot_mat_3x3[0][1], 0],
        [rot_mat_3x3[1][2], rot_mat_3x3[1][0], rot_mat_3x3[1][1], 0],
        [0, 0, 0, 1]
    ])
    return trans_matrix @ rot_matrix

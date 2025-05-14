## @file general_functions.py
# @author Zuzana Miškaňová
# @brief Contains some mathematical functions for calculating matrices and rotations.

import numpy as np
from scipy.spatial.transform import Rotation

from params import NEAR_PLANE, FAR_PLANE

## @brief Creates a Deck.gl-style projection matrix according to camera parameters.
# @param camera_params_dict A dictionary with camera parameters such as loaded from file data/camera_azd.yaml.
# @param K A custom calibration matrix.
# @param far_plane A custom distance of the far plane.
# @return The calculated projection matrix.
def calculate_projection_matrix(camera_params_dict, K=np.array([]), far_plane=None):
    w = camera_params_dict['Camera.width']
    h = camera_params_dict['Camera.height']

    if K.any():  # a special calibration matrix is given
        f_x = K[0][0]
        f_y = K[1][1]
        c_x = K[0][2]
        c_y = K[1][2]
    else:
        f_x = camera_params_dict['CameraMat']['data'][0]
        f_y = camera_params_dict['CameraMat']['data'][4]
        c_x = camera_params_dict['CameraMat']['data'][2]
        c_y = camera_params_dict['CameraMat']['data'][5]

    if far_plane != None:
       f = far_plane
    else:
        f = FAR_PLANE
    n = NEAR_PLANE

    proj_mat = np.array([
        [2 * f_x / w,            0,   2 * c_x / w - 1,                    0],
        [          0,  2 * f_y / h,   2 * c_y / h - 1,                    0],
        [          0,            0,  -(f + n)/(f - n), -(2 * f * n)/(f - n)],
        [          0,            0,                -1,                    0] 
    ])
    return proj_mat.transpose().flatten()


## @brief Calculates a transformation matrix for train profile positioning.
# It is needed to translate the frame to "trans_point" and then rotate around that point.
# That is equivalent to rotating around [0, 0, 0] and then translating to "trans_point".
# @param trans_point The position to which the profile needs to be translated.
# @param rot_mat_3x3 The rotation that needs to be applied to the profile.
# @return The calculated transformation matrix.
def calculate_train_profile_transformation_matrix(trans_point, rot_mat_3x3):
    trans_matrix = np.array([
        [1, 0, 0, trans_point[0]],
        [0, 1, 0, trans_point[1]],
        [0, 0, 1, trans_point[2]],
        [0, 0, 0, 1]
    ])
    rot_matrix = np.array([
        [rot_mat_3x3[0][0], rot_mat_3x3[0][1], rot_mat_3x3[0][2], 0],
        [rot_mat_3x3[1][0], rot_mat_3x3[1][1], rot_mat_3x3[1][2], 0],
        [rot_mat_3x3[2][0], rot_mat_3x3[2][1], rot_mat_3x3[2][2], 0],
        [0, 0, 0, 1]
    ])
    return trans_matrix @ rot_matrix


## @brief Loads rotation from the format in the files (xzy, in degrees) into a Rotation object.
# (If translations are in order yzx instead of xyz, then rotations are in order xzy instead of zyx.)
# @param rot_raw A rotation in euler angles, xzy format.
# @return A Rotation object.
def load_rotation(rot_raw):
    return Rotation.from_euler("xzy", rot_raw, degrees=True)


## @brief Converts a Rotation object to inverse euler angles (for the camera).
# @param rotation A Rotation object.
# @return A rotation in euler angles, zyx format.
def rotation_to_euler(rotation):
    rotation_zyx = rotation.inv().as_euler("zyx", degrees=True)
    return [-rotation_zyx[0], rotation_zyx[1], -rotation_zyx[2]]


## @brief Converts a Rotation object to a rotation matrix.
# @param rotation A Rotation object.
# @return A rotation matrix.
def rotation_to_matrix(rotation):
    return rotation.as_matrix()


## @brief Converts a Rotation object to an inverted rotation matrix.
# @param rotation A Rotation object.
# @return An inverted rotation matrix.
def rotation_to_inv_matrix(rotation):
    return rotation.inv().as_matrix()

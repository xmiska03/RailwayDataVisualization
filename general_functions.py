import numpy as np
from scipy.spatial.transform import Rotation

from params import NEAR_PLANE, FAR_PLANE

# creates a deck.gl-style projection matrix according to camera parameters
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

# calculates camera position offset according to the extrinsic matrix
def calculate_translation_from_extr_mat(camera_params_dict):
    # extracts T from matrix E = RT
    extr_mat = camera_params_dict['ExtrinsicMat']['data']
    extr_fourth_col = np.array([extr_mat[3], extr_mat[7], extr_mat[11]]).transpose()
    R = np.array([
        [extr_mat[0], extr_mat[1], extr_mat[2]],
        [extr_mat[4], extr_mat[5], extr_mat[6]],
        [extr_mat[8], extr_mat[9], extr_mat[10]]
    ])
    T = np.matmul(np.linalg.inv(R), extr_fourth_col) * -1
    return [T[2], T[0], T[1]]

# function used for train profile positioning
# it is needed to translate the frame to "trans_point" and then rotate around that point
# that is equivalent to rotating around [0, 0, 0] and then translating to "trans_point"
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

# loads rotation from the format in the files (xzy, in degrees) into a Rotation object
# if translations are in order yzx instead of xyz, then rotations are in order xzy instead of zyx
def load_rotation(rot_raw):
    return Rotation.from_euler("xzy", rot_raw, degrees=True)

# converts Rotation object to inverse euler angles (for the camera)
def rotation_to_euler(rotation):
    rotation_zyx = rotation.inv().as_euler("zyx", degrees=True)
    return [-rotation_zyx[0], rotation_zyx[1], -rotation_zyx[2]]

# converts Rotation object to rotation matrix
def rotation_to_matrix(rotation):
    return rotation.as_matrix()

# converts Rotation object to inverted rotation matrix
def rotation_to_inv_matrix(rotation):
    return rotation.inv().as_matrix()

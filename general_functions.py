import numpy as np


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

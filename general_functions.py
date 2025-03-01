import numpy as np


# creates transformation matrix from translation and rotation data
def calculate_transformation_matrix(trans, rot_mat_3x3):
    trans_matrix = np.array([
        [1, 0, 0, -trans[2]],
        [0, 1, 0, -trans[0]],
        [0, 0, 1, -trans[1]],
        [0, 0, 0, 1]
    ])
    #rotation = Rotation.from_euler("xyz", rot_matrix, degrees=True)
    #rot_mat_3x3 = rotation.as_matrix()
    rot_matrix = np.array([
        [rot_mat_3x3[2][2], rot_mat_3x3[2][0], rot_mat_3x3[2][1], 0],
        [rot_mat_3x3[0][2], rot_mat_3x3[0][0], rot_mat_3x3[0][1], 0],
        [rot_mat_3x3[1][2], rot_mat_3x3[1][0], rot_mat_3x3[1][1], 0],
        [0, 0, 0, 1]
    ])
    return rot_matrix @ trans_matrix

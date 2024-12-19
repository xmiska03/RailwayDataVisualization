from pypcd4 import PointCloud
import numpy as np
import csv
import cv2
from scipy.spatial.transform import Rotation

IMAGE_MAX_X = 2048
IMAGE_MAX_Y = 1536


def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)


def create_image(pc_nparray):
    # create a new black image
    img = np.zeros(shape=(IMAGE_MAX_Y, IMAGE_MAX_X), dtype=np.uint32)

    # retype the coordinates (and intensity) to int
    pc_nparray = pc_nparray.astype(int)

    # filter out the points that are out of bounds
    filter_array = [(0 <= point[0] < IMAGE_MAX_X and 0 <= point[1] < IMAGE_MAX_Y) for point in pc_nparray]
    pc_nparray = pc_nparray[filter_array]
 
    # multiply intensity
    intensity_array = pc_nparray[:, 3] * 1000

    # revert the axes
    img_x_array = IMAGE_MAX_X - 1 - pc_nparray[:, 0]
    img_y_array = IMAGE_MAX_Y - 1 - pc_nparray[:, 1]

    # plot the points into the image
    np.add.at(img, (img_y_array, img_x_array), intensity_array)

    img = np.clip(img, 0, 32767).astype(np.uint16)
    return img


def generate_frame(pc_nparray, position, outdir):
    # apply translation
    pc_nparray -= np.append(trans_nparray[position], 0)

    # shift the camera right (so that it is over the trails)
    #pc_nparray += [1.3, 0, 0, 0]
    
    # create rotation matrix
    rotation = Rotation.from_euler("xyz", rot_nparray[position], degrees=True)
    rot_matrix_3x3 = rotation.as_matrix()
    rot_matrix_3x4 = np.hstack((rot_matrix_3x3, np.zeros((3, 1))))
    rot_matrix_4x4 = np.vstack((rot_matrix_3x4, [[0, 0, 0, 1]]))

    # apply rotation
    pc_nparray = pc_nparray @ rot_matrix_4x4.T

    # filter out the points that are behind the camera
    filter_array = [(row[2] > 0) for row in pc_nparray]
    pc_nparray = pc_nparray[filter_array]

    # apply projection
    z = pc_nparray[:, 2:3]
    divide_by_z_array = np.hstack((z, z, z, np.ones(shape=(z.shape[0], 1))))
    pc_nparray = np.divide(pc_nparray, divide_by_z_array)

    # transform to pixel coordinates
    pc_nparray = pc_nparray @ intrinsic_matrix_4x4.T

    # create image
    img = create_image(pc_nparray)

    # write image to file
    cv2.imwrite(f"output/{outdir}/{position}.png", img)


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# change the order of the axes (zxy -> xyz) in the point cloud
pc_nparray = pc_nparray[:, [1, 2, 0, 3]]

# load trasnformation data
trans_nparray = load_csv_into_nparray("data/trans.csv")
rot_nparray = load_csv_into_nparray("data/rot.csv")
intrinsic_matrix_3x3 = load_csv_into_nparray("data/K.csv")
intrinsic_matrix_3x4 = np.hstack((intrinsic_matrix_3x3, np.zeros((3, 1))))
intrinsic_matrix_4x4 = np.vstack((intrinsic_matrix_3x4, [[0, 0, 0, 1]]))

# number of frames to generate (500 in example data)
frames_cnt = trans_nparray.shape[0]


# generate 500 images
for i in range(0, frames_cnt, 1):
    pc_nparray_copy = np.copy(pc_nparray)
    generate_frame(pc_nparray_copy, i, "optimized")
    print("Generated", i)

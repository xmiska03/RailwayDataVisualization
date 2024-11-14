from pypcd4 import PointCloud
import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

IMAGE_MAX_X = 2048
IMAGE_MAX_Y = 1536

PROJECTION_MATRIX = np.array([[1, 0, 0, 0], \
                              [0, 1, 0, 0], \
                              [0, 0, 1, 0], \
                              [0, 0, 0.05, 1]])

def create_image(pc_array):
    # create a new black image
    img = np.zeros(shape=(IMAGE_MAX_Y, IMAGE_MAX_X), dtype=np.int16)

    # calculate a scale to plot points into pixels of the image
    column_x = pc_array[:, 0]
    column_y = pc_array[:, 1]
    x_min, x_max = min(column_x), max(column_x)
    y_min, y_max = min(column_y), max(column_y)
    x_scale = (IMAGE_MAX_X - 1) / (x_max - x_min)
    y_scale = (IMAGE_MAX_Y - 1) / (y_max - y_min)
    img_scale = min(x_scale, y_scale)

    # plot the points into the image
    for point in pc_array:
        if (point[2] > 0):  # if z > 0
            x = int((point[0] - x_min) * img_scale)
            y = int((point[1] - y_min) * img_scale)
            intensity = point[3]
            # add intensity to pixel value, prevent overflow of int16
            if (32767 - img[IMAGE_MAX_Y-y-1][x] > intensity):
                img[IMAGE_MAX_Y-y-1][x] += intensity
            else:
                img[IMAGE_MAX_Y-y-1][x] = 32767
    return img


def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_array = pc.numpy(("x", "y", "z", "intensity"))

# change the order of the axes (zxy -> xyz) in the point cloud
for point in pc_array:
    z = point[0]
    point[0] = point[1]
    point[1] = point[2]
    point[2] = z

# load transformation matrices
trans_array = load_csv_into_nparray("data/trans.csv")
rot_array = load_csv_into_nparray("data/rot.csv")
calib_matrix = load_csv_into_nparray("data/K.csv")
    
# create rotation matrix
rotation = Rotation.from_euler("xyz", rot_array[0], degrees=False)
rot_matrix3 = rotation.as_matrix()

# transform all the points in the point cloud
for i in range(pc_array.shape[0]):
    # transform from world space to view space
    point3 = np.array(pc_array[i][0:3])
    point3[0] += 1
    #point3[1] -= 1
    #point3[2] -= 5
    point3[0] -= trans_array[0][0]
    point3[1] -= trans_array[0][1]
    point3[2] -= trans_array[0][2]
    #point3 = rot_matrix3 @ point3

    # projection (transform from world space to clip space)
    point4 = np.array([point3[0], point3[1], point3[2], 1]) # homogenous coords
    point4 = PROJECTION_MATRIX @ point4
    # normalisation
    point4[0] /= point4[3]
    point4[1] /= point4[3]
    point4[2] /= point4[3]
    
    pc_array[i][0] = point4[0]
    pc_array[i][1] = point4[1]
    pc_array[i][2] = point4[2]

# create image
img = create_image(pc_array)

# tresholding for better visibility

avg = int(np.average(img))
for y in range(1536):
    for x in range(2048):
        if (img[y][x] > avg):
            img[y][x] = 20000


# show the image
plt.imshow(img, cmap = "gray")
plt.show()

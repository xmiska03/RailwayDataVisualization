from pypcd4 import PointCloud
import numpy as np
import csv
import cv2
from scipy.spatial.transform import Rotation

IMAGE_MAX_X = 2048
IMAGE_MAX_Y = 1536

PROJECTION_MATRIX = np.array([[1, 0, 0, 0], \
                              [0, 1, 0, 0], \
                              [0, 0, 1, 0], \
                              [0, 0, 1, 1]])


def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)


def create_image(pc_array):
    # create a new black image
    img = np.zeros(shape=(IMAGE_MAX_Y, IMAGE_MAX_X), dtype=np.uint16)

    # plot the points into the image
    for point in pc_array:
        if (point[3] > 0):  # if intensity > 0
            x = int(point[0])
            y = int(point[1])

            if (x < 0 or x >= IMAGE_MAX_X or y < 0 or y >= IMAGE_MAX_Y):
                continue
            intensity = point[3]
            # add intensity to pixel value, prevent overflow of int16
            if (32767 - img[IMAGE_MAX_Y-y-1][IMAGE_MAX_X-x-1] > intensity * 1000):
                img[IMAGE_MAX_Y-y-1][IMAGE_MAX_X-x-1] += intensity * 1000
            else:
                img[IMAGE_MAX_Y-y-1][IMAGE_MAX_X-x-1] = 32767
    return img


def generate_frame(position):
    # create rotation matrix
    rotation = Rotation.from_euler("xyz", rot_array[position], degrees=True)
    ROT_MATRIX = rotation.as_matrix()

    new_pc_array = np.zeros(shape=(pc_array.shape[0], 4))

    # transform all the points in the point cloud
    for i in range(pc_array.shape[0]):
        # transform from world space to view space
        point3 = np.array(pc_array[i][0:3])
        #point3[0] += 1.5
        #point3[1] -= 1
        #point3[2] -= 5
        point3[0] -= trans_array[position][0]
        point3[1] -= trans_array[position][1]
        point3[2] -= trans_array[position][2]
        point3 = ROT_MATRIX @ point3

        # homogenous coords
        point4 = np.array([point3[0], point3[1], point3[2], 1])

        # if the point is behind the camera, change intensity to 0
        if (point4[2] < 0):
            pc_array[i][3] = 0
        
        # projection (transform from world space to clip space)
        point4 = PROJECTION_MATRIX @ point4
        
        # normalisation
        point4[0] /= point4[3]
        point4[1] /= point4[3]
        point4[2] /= point4[3]

        # multiply by calibration matrix
        point4[0:3] = INTRINSIC_MATRIX @ point4[0:3]
        
        # write back to array
        new_pc_array[i][0] = point4[0]
        new_pc_array[i][1] = point4[1]
        new_pc_array[i][2] = point4[2]
        new_pc_array[i][3] = pc_array[i][3]

    # create image
    img = create_image(new_pc_array)

    # tresholding for better visibility
    """avg = int(np.average(img))
    for y in range(1536):
        for x in range(2048):
            if (img[y][x] > avg):
                img[y][x] = 20000"""

    #print(cv2.getBuildInformation())
    cv2.imwrite(f"generated/{position}.png", img)
    
    # show the image
    #plt.imshow(img, cmap = "gray")
    #plt.show()


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
INTRINSIC_MATRIX = load_csv_into_nparray("data/K.csv")

# generate 500 images
for i in range(0, trans_array.shape[0], 50):
    generate_frame(i)
    print("Generated", i)
from pypcd4 import PointCloud
import numpy as np
import cv2
import csv
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)

pc : PointCloud = PointCloud.from_path("data/scans.pcd")
pc_array : np.ndarray = pc.numpy(("x", "y", "z", "intensity"))

print("Analysis:")
print(pc.fields, pc_array.shape)
column_x = pc_array[:, 0]
column_y = pc_array[:, 1]
column_z = pc_array[:, 2]
column_i = pc_array[:, 3]
    
print("\nmin, avg, max of the columns: ")
print(min(column_x), np.average(column_x), max(column_x))
print(min(column_y), np.average(column_y), max(column_y))
print(min(column_z), np.average(column_z), max(column_z))
print(min(column_i), np.average(column_i), max(column_i))

# load transformation matrices
trans_array = load_csv_into_nparray("data/trans.csv")
rot_array = load_csv_into_nparray("data/rot.csv")
calib_matrix = load_csv_into_nparray("data/K.csv")


trans_matrix = np.identity(4, dtype=float)
trans_matrix[0][3] = trans_array[0][0]
trans_matrix[1][3] = trans_array[0][1]
trans_matrix[2][3] = trans_array[0][2]

rotation = Rotation.from_euler("xyz", rot_array[0], degrees=False)
rot_matrix3 = rotation.as_matrix()  
print(rot_matrix3)


# transform 3x3 matrix to 4x4 matrix (homogenous coordinates) 
rot_matrix = np.array([[rot_matrix3[0][0], rot_matrix3[0][1], rot_matrix3[0][2], 0], \
                       [rot_matrix3[1][0], rot_matrix3[1][1], rot_matrix3[1][2], 0], \
                       [rot_matrix3[2][0], rot_matrix3[2][1], rot_matrix3[2][2], 0], \
                       [0, 0, 0, 1]])
projection_matrix = np.array([[1, 0, 0, 0], \
                              [0, 1, 0, 0], \
                              [0, 0, 1, 0], \
                              [0, 0, 20, 1]])
# print(rot_matrix)

# transf_matrix = rot_matrix @ np.linalg.inv(trans_matrix)
# print(transf_matrix)

# y - bod v souradnem systemu kamery, x - bod ve "world coordinates"
# x = RTy
# y = (RT)^-1 x


# transform all the points in the point cloud
for i in range(pc_array.shape[0]):
    # transform to local coords
    point3 = np.array(pc_array[i][0:3])
    #point3 -= trans_array[0]
    #point3 = rot_matrix3 @ point3

    pc_array[i][0] = point3[0]
    pc_array[i][1] = point3[1]
    pc_array[i][2] = point3[2]




# print("Analysis after transformation:")
# print(pc.fields, pc_array.shape)
column_x = pc_array[:, 0]
column_y = pc_array[:, 1]
column_z = pc_array[:, 2]
x_min, x_max = min(column_x), max(column_x)
y_min, y_max = min(column_y), max(column_y)
z_min, z_max = min(column_z), max(column_z)

camerax = int((trans_array[0][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[0][1] - y_min) / (y_max - y_min) * 1535)
print("ZY first camera position: ", camerax, 1535-cameray)
camerax = int((trans_array[250][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[250][1] - y_min) / (y_max - y_min) * 1535)
print("middle camera position: ", camerax, 1535-cameray)
camerax = int((trans_array[499][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[499][1] - y_min) / (y_max - y_min) * 1535)
print("last camera position: ", camerax, 1535-cameray)

camerax = int((trans_array[0][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[0][0] - y_min) / (y_max - y_min) * 1535)
print("ZX first camera position: ", camerax, 1535-cameray)
camerax = int((trans_array[250][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[250][0] - y_min) / (y_max - y_min) * 1535)
print("middle camera position: ", camerax, 1535-cameray)
camerax = int((trans_array[499][2] - x_min) / (x_max - x_min) * 2047)
cameray = int((trans_array[499][0] - y_min) / (y_max - y_min) * 1535)
print("last camera position: ", camerax, 1535-cameray)

# create a new black image
img = np.zeros(shape=(1536,2048), dtype=np.int16)

# plot the points into the image
for point in pc_array:
    #if (point[0] > 0):  # if x > 0
        # pinhole camera model
        point4 = np.array([point[0], point[1], point[2], 1]) # homogenous coords
        coords = pinhole_matrix @ point4
        # normalisation
        #coords[0] = coords[0]/coords[3]
        #coords[1] = coords[1]/coords[3]
        #coords[1] = coords[2]/coords[3]

        #print(coords[0], coords[1])
        #print(point[0], point[1])

        x = int((coords[0] - x_min) / (x_max - x_min) * 2047)
        y = int((coords[1]- y_min) / (y_max - y_min) * 1535)
        i = point[3]
        if (0 < x < 2047 and 0 < y < 1535):
            if (img[1535-y][x] < 20000):
                img[1535-y][x] += i * 10


print("average: ", min(img.ravel()), max(img.ravel()), np.average(img))
for y in range(1536):
    for x in range(2048):
        if (img[y][x] > 1):
            img[y][x] = 20000
"""

# print("Analysis after transformation:")
# print(pc.fields, pc_array.shape)
column_x = pc_array[:, 0]
column_y = pc_array[:, 1]
x_min, x_max = min(column_x), max(column_x)
y_min, y_max = min(column_y), max(column_y)

# create a new black image
img = np.zeros(shape=(1536,2048), dtype=np.int16)

# plot the points into the image
for point in pc_array:
    #if (point[2] > 0):  # if z > 0

        # pinhole camera model
        point4 = np.array([point3[0], point3[1], point3[2], 1]) # homogenous coords
        coords = pinhole_matrix @ point4
        
        #x = (point[0] - x_min) / (x_max - x_min) * 2047
        #y = (point[1] - y_min) / (y_max - y_min) * 1535
        i = point[3]
        if (-1000 < coords[0] < 1000 and -700 < coords[1] < 700):
            img[coords[0] + 1000][coords[1] + 700] += i * 10
    
print("average: ", min(img.ravel()), max(img.ravel()), np.average(img))
for y in range(1536):
    for x in range(2048):
        if (img[y][x] > 0.01):
            img[y][x] = 20000
"""

# show the image
plt.imshow(img, cmap = "gray")
plt.show()

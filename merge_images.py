# Merges two greyscale images to compare them.

import numpy as np
import cv2


# load two greytone images (of the same size)
img1 = cv2.imread("data/0.png")                 # red
img2 = cv2.imread("output/shifted_left/0.png")     # blue

# create a new black image with 3 color channels
merge_img = np.zeros(shape=(img1.shape[0], img1.shape[1], 3), dtype=np.uint8)

# write pixels from img1 in red color
for i in range(img1.shape[0]):
    for j in range(img1.shape[1]):
        merge_img[i][j][2] = img1[i][j][0]

# write pixels from img2 in blue color
for i in range(img2.shape[0]):
    for j in range(img2.shape[1]):
        merge_img[i][j][0] = img2[i][j][0]

# write result to file
cv2.imwrite("output/merge.png", merge_img)
import numpy as np
import cv2


# load greytone image
img1 = cv2.imread("output/shifted_left/0.png")

# create a new black image with 3 color channels
inv_img = np.zeros(shape=(img1.shape[0], img1.shape[1], 3), dtype=np.uint8)

# create a black-white image with inverted colors
for i in range(img1.shape[0]):
    for j in range(img1.shape[1]):
        if img1[i][j][0] > 2:
            inv_img[i][j] = [0, 0, 0]
        else:
            inv_img[i][j] = [255, 255, 255]

# write result to file
cv2.imwrite("output/invres0.png", inv_img)
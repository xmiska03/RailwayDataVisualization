# Creates an image which demonstrates the effect of camera distortion with particular coefficients.

import numpy as np
import cv2

# distortion coefficients
K1 = -0.1832170424487164 
K2 = 0.02691675026209955
P1 = -0.001191374354805736
P2 = 0.000804309339521888
K3 = 0.3354456739081583

# parameters of the image
SHAPE = (1536, 2048)
LINE_WIDTH = 3
# horizontal and vertical lines
hor_lines = [int(SHAPE[0]*1/8), int(SHAPE[0]*2/8), int(SHAPE[0]*3/8), int(SHAPE[0]*4/8), \
             int(SHAPE[0]*5/8), int(SHAPE[0]*6/8), int(SHAPE[0]*7/8)]
ver_lines = [int(SHAPE[1]*1/8), int(SHAPE[1]*2/8), int(SHAPE[1]*3/8), int(SHAPE[1]*4/8), \
             int(SHAPE[1]*5/8), int(SHAPE[1]*6/8), int(SHAPE[1]*7/8)]


# create a 2 new black image with 3 color channels
grid_img = np.zeros(shape=(SHAPE[0], SHAPE[1], 3), dtype=np.uint8)
dist_grid_img = np.zeros(shape=(SHAPE[0], SHAPE[1], 3), dtype=np.uint8)

# loop through all pixels and create a grid in both images
for i in range(SHAPE[0]):
    for j in range(SHAPE[1]):
        if min([abs(a - i) for a in hor_lines]) < LINE_WIDTH \
          or min([abs(a - j) for a in ver_lines]) < LINE_WIDTH:
            dist_grid_img[i][j][0] = 240   # light blue grid for the final image
            dist_grid_img[i][j][1] = 170
            dist_grid_img[i][j][2] = 145
            grid_img[i][j][0] = 255        # whatever, does not matter
        else:
            dist_grid_img[i][j][0] = 255   # white background for the final image
            dist_grid_img[i][j][1] = 255
            dist_grid_img[i][j][2] = 255


# loop through grid_img, distort the grid and write the result into dist_grid_img
for y in range(SHAPE[0]):
    for x in range(SHAPE[1]):
        if grid_img[y][x][0] == 255:
            # this pixel is a part of the grid
            # convert to normalized image coordinates
            y_norm = (y - int(SHAPE[0]/2)) / SHAPE[1]
            x_norm = (x - int(SHAPE[1]/2)) / SHAPE[1]
            r_pow2 = x_norm*x_norm + y_norm*y_norm    # r^2
            
            # count the radial distortion
            px_coef = (1 + K1*r_pow2 + K2*r_pow2*r_pow2 + K3*r_pow2*r_pow2)
            x_dist_norm = x_norm * px_coef
            y_dist_norm = y_norm * px_coef

            # count the tangential distortion
            #x_dist_norm = x_norm + (2*P1*x_norm*y_norm + P2*(r_pow2 + 2*x_norm*x_norm))
            #y_dist_norm = y_norm + (P1*(r_pow2 + 2*y_norm*y_norm) + 2*P1*x_norm*y_norm)

            # convert back from normalized image coordinates to pixels
            y_dist = int(y_dist_norm * SHAPE[1] + int(SHAPE[0]/2))
            x_dist = int(x_dist_norm * SHAPE[1] + int(SHAPE[1]/2))

            # write the distorted pixel in black color
            if (0 <= y_dist < SHAPE[0] and 0 <= x_dist < SHAPE[1]):
                dist_grid_img[y_dist][x_dist][0] = 0    # black
                dist_grid_img[y_dist][x_dist][1] = 0
                dist_grid_img[y_dist][x_dist][2] = 0


# write result to file
cv2.imwrite("distorted_grid_only_radial.png", dist_grid_img)
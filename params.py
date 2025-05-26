## @file params.py
# @author Zuzana Miškaňová
# @brief Contains the default workspace settings of the visualization.


## @brief Initial size of points in the point cloud.
POINT_SIZE = 20
## @brief Initial opacity of the point cloud layer.
OPACITY = 0.6
## @brief Initial boundaries of the color scale for the point cloud.
COLOR_SCALE_BOUNDARIES = [0, 20]

## @brief Initial line width of the vector data and the train profile line layer.
LINE_WIDTH = 3
## @brief Initial line width of the train profile layer.
PROFILE_WIDTH = 3
## @brief Initial color of the vector data layer.
LINE_COLOR = {"rgb": [250, 101, 15], "hex": "#fa650f"}
## @brief Initial color of the train profile layer.
PROFILE_COLOR = {"rgb": [225, 80, 255], "hex": "#e250ff"}
## @brief Initial color of the train profile line layer.
PROFILE_LINE_COLOR = {"rgb": [232, 175, 16], "hex": "#e8af10"}

## @brief Distance of the near plane.
NEAR_PLANE = 0.1
## @brief Initial distance of the far plane.
FAR_PLANE = 300
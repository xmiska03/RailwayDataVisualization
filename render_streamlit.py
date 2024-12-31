import streamlit as st
from pypcd4 import PointCloud
import pandas as pd
import numpy as np
import pydeck


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# create a pandas DataFrame
pc_dict = {
  "x": pc_nparray[:, 1],
  "y": pc_nparray[:, 2],
  "z": 100000 - pc_nparray[:, 0] * -100000,
  "r": pc_nparray[:, 3] * 6
}
pc_df = pd.DataFrame(pc_dict)

point_cloud_layer = pydeck.Layer(
    "PointCloudLayer",
    data=pc_df,
    get_position=["x", "y", "z"],
    get_color=[255, "r", "r", 125],
    get_normal=[0, 0, 0],
    auto_highlight=True,
    pickable=True,
    point_size=1,
)

view_state = pydeck.ViewState(target=[10000, 10000, 0], controller=True, latitude=0, longitude=90, rotation_orbit=90, rotation_x=0, zoom=1)
# Streamlit does not support views other than MapView
# view = pydeck.View(type="OrbitView", controller=True, near=5, far=300, fovy=20)

st.pydeck_chart(
    pydeck.Deck(
        initial_view_state=view_state,
        layers=[
            point_cloud_layer
        ],
        map_provider=None
    ),
    use_container_width=True
)

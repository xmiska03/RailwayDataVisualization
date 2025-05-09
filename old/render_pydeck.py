from pypcd4 import PointCloud
import numpy as np
import pydeck
import pandas as pd


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])

point_cloud_layer = pydeck.Layer(
    "PointCloudLayer",
    data=pc_df,
    get_position=["x", "y", "z"],
    get_color=["r * 6", "r * 6", "r * 6", 125],
    get_normal=[0, 0, 0],
    auto_highlight=True,
    pickable=True,
    point_size=25,
)

#view_state = pydeck.ViewState(target=[5.7, -0.08 - 1.3, -0.07], controller=True, rotation_orbit=90, rotation_x=0, zoom=10)
#view = pydeck.View(type="OrbitView", controller=True, near=5, far=300, fovy=50)

view_state = pydeck.ViewState(position=[5.7, -0.08 - 1.3, -0.07], bearing=90, controller=True)
view = pydeck.View(type="FirstPersonView", controller=True, fovy=20)

r = pydeck.Deck(point_cloud_layer, initial_view_state=view_state, views=[view])
r.to_html("output/pydeck/pc_pydeck.html", css_background_color="#add8e6")


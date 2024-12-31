import dash
from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd
import numpy as np
from pypcd4 import PointCloud


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])

point_cloud_layer = pdk.Layer(
    "PointCloudLayer",
    data=pc_df,
    get_position=["x", "y", "z"],
    get_color=["r * 6", "r * 6", "r * 6", 125],
    get_normal=[0, 0, 0],
    auto_highlight=True,
    pickable=True,
    point_size=30,
)

view_state = pdk.ViewState(target=[5.7, -0.08 - 1.3, -0.07], rotation_orbit=90, controller=True, zoom=10)
view = pdk.View(type="OrbitView", controller=True, fovy=20)

deck = pdk.Deck(
    initial_view_state=view_state,
    views=[view],
    layers=[point_cloud_layer]
)

deck_json = deck.to_json()

# create a Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            "Dash Point Cloud Visualization",
            style={"textAlign": "center", "color": "black"}
        ),
        dash_deck.DeckGL(
            data=deck_json,
            style={"height": "90vh", "width": "100%", "marginLeft": "5%"}
        ),
    ],
    style={
        "backgroundImage": "url(/assets/rails_photo.png)",
        "backgroundSize": "cover",
        "backgroundRepeat": "no-repeat",
        "backgroundPosition": "center",
        "height": "100vh",
        "width": "100vw",
        "margin": "0",
        "padding": "0",
    },
)

if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from dash import html, dcc, callback, Output, Input
import dash_deck
import pydeck as pdk
import pandas as pd
import numpy as np
from pypcd4 import PointCloud


# visualization parameters
POINT_SIZE = 40
TARGET = [5.7, -0.08 - 0.8, -0.07 + 1]
ROTATION_ORBIT = 90
ZOOM = 10
FOVY = 30


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])

point_cloud_layer = pdk.Layer(
    "PointCloudLayer",
    data=pc_df,
    get_position=["x", "y", "z"],
    get_color=["intensity * 6", 0, "255 - intensity * 6", 125],
    get_normal=[0, 0, 0],
    auto_highlight=True,
    pickable=True,
    point_size=POINT_SIZE,
)

view_state = pdk.ViewState(target=TARGET, rotation_orbit=ROTATION_ORBIT, controller=True, zoom=ZOOM)
view = pdk.View(type="OrbitView", controller=True, fovy=FOVY)

deck = pdk.Deck(
    initial_view_state=view_state,
    views=[view],
    layers=[point_cloud_layer],
    map_provider=None,
    map_style=None
)

deck_json = deck.to_json()    # creates a string

# create a Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=
    [
        html.H1(
            "Vizualizace dat z mobilního mapovacího systému",
            style={"textAlign": "center", "color": "black"}
        ),
        dcc.Slider(0, 500, 1, value=0, marks={0:'0', 500:'500'}, id='camera-position-slider'),
        html.Div(
            [
                dash_deck.DeckGL(
                data=deck_json,
                style={"height": "80vh", 
                    "width": "80vw", 
                    "marginLeft": "0%", 
                    "marginTop": "7%"},
                id="point-cloud-visualization"
                ),
            ], style = {
                "backgroundImage": "url(/assets/rails_photo.png)",
                "backgroundSize": "cover",
                "backgroundRepeat": "no-repeat",
                "backgroundPosition": "center",
                "height": "80vh",
                "width": "80vw",
                "margin": "0",
                "padding": "0",  
            }

        )
    ],
    style={
        "height": "100vh",
        "width": "80vw",
        "margin": "0",
        "padding": "0",
    },
)


# the logic of the app
@callback(
    Output(component_id='point-cloud-visualization', component_property='data'),
    Input(component_id='camera-position-slider', component_property='value')
)
def shift_camera(new_pos):
    new_target = TARGET[:]
    new_target[0] += new_pos * 0.5
    view_state=pdk.ViewState(target=new_target, rotation_orbit=ROTATION_ORBIT, controller=True, zoom=ZOOM)
    deck = pdk.Deck(
        initial_view_state=view_state,
        views=[view],
        layers=[point_cloud_layer],
        map_provider=None,
        map_style=None
    )
    return deck.to_json()

if __name__ == "__main__":
    app.run(debug=True)

from dash import Dash, html, dcc, callback, Output, Input, Patch, clientside_callback
import dash_deck
import pandas as pd
import numpy as np
from pypcd4 import PointCloud
import csv
from scipy.spatial.transform import Rotation


# visualization parameters
POINT_SIZE = 50
TARGET = [0, -0.3, 1.0]      # move the camera left/right, up/down
ROTATION_ORBIT = 91.5        # turn the camera left/right
ROTATION_X = 4.1             # turn the camera up/down
ZOOM = 10
FOVY = 21                    # focal length
FAR_PLANE = 300
TRANSPARENCY = 90
ANIMATION_SPEED = 1         # frames per second
ANIMATION_FRAMES_STEP = 10


# loads a csv file into a numpy array
def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)
    
# creates transformation matrix from translation and rotation data
def calculate_transformation_matrix(trans_nparray, rot_nparray, position):
    trans_matrix = np.array([
        [1, 0, 0, -trans_nparray[position][2]],
        [0, 1, 0, -trans_nparray[position][0]],
        [0, 0, 1, -trans_nparray[position][1]],
        [0, 0, 0, 1]
    ])
    rotation = Rotation.from_euler("xyz", rot_nparray[position], degrees=True)
    rot_mat_3x3 = rotation.as_matrix()
    rot_matrix = np.array([
        [rot_mat_3x3[2][2], rot_mat_3x3[2][0], rot_mat_3x3[2][1], 0],
        [rot_mat_3x3[0][2], rot_mat_3x3[0][0], rot_mat_3x3[0][1], 0],
        [rot_mat_3x3[1][2], rot_mat_3x3[1][0], rot_mat_3x3[1][1], 0],
        [0, 0, 0, 1]
    ])
    return rot_matrix @ trans_matrix

# creates transformation function to pass to pydeck
def create_transformation_string(transf_mat):
    return (f"x * {transf_mat[0][0]} + y * {transf_mat[0][1]} + z * {transf_mat[0][2]} "
            f"+ {transf_mat[0][3]}, "
            f"x * {transf_mat[1][0]} + y * {transf_mat[1][1]} + z * {transf_mat[1][2]} "
            f"+ {transf_mat[1][3]}, "
            f"x * {transf_mat[2][0]} + y * {transf_mat[2][1]} + z * {transf_mat[2][2]} "
            f"+ {transf_mat[2][3]}"
    )


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

#pc_nparray = pc_nparray[:20000]

# load data about camera positions (order of the columns: y, z, x)
trans_nparray = load_csv_into_nparray("data/trans.csv")
rot_nparray = load_csv_into_nparray("data/rot.csv")

# number of frames to generate (500 in example data)
frames_cnt = trans_nparray.shape[0]

# pre-calculate all transformation strings
transf_strings = []
for i in range(frames_cnt):
    transf_mat = calculate_transformation_matrix(trans_nparray, rot_nparray, i)
    transf_strings.append(create_transformation_string(transf_mat))

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])

# prepare the visualization of the point cloud using Deck.GL
point_cloud_layer = {
    "@@type": "PointCloudLayer",
    "data": pc_df.to_dict(orient="records"),
    "getColor": (
        "@@=[intensity > 6 ? 7 * (intensity - 6) : 0, "
        "intensity > 6 ? 255 - 7 * (intensity - 6) : 51 * (intensity - 6), "
        f"intensity > 6 ? 0 : 255 - 51 * (intensity - 6), {TRANSPARENCY}]"
    ),
    "getPosition": f"@@=[{transf_strings[0]}]",
    "pointSize": POINT_SIZE,
    "transitions": {
        "getPosition": 1000
      }
}

view_state = {
    "rotationOrbit": ROTATION_ORBIT,
    "rotationX": ROTATION_X,
    "target": TARGET,
    "zoom": ZOOM
}

view = {
    "@@type": "OrbitView",
    "far": FAR_PLANE,
    "fovy": FOVY
}

deck_dict = {
    "initialViewState": view_state,
    "views": [view],
    "layers": [point_cloud_layer],
}

# create a Dash app
app = Dash(__name__)

app.layout = html.Div(children=
    [
        dcc.Interval(
            id="animation-interval", 
            interval=1000/ANIMATION_SPEED, 
            n_intervals=0,   # begin from 0
            max_intervals=frames_cnt/ANIMATION_FRAMES_STEP
        ),
        html.H1(
            "Vizualizace dat z mobilního mapovacího systému",
            style={"textAlign": "center", "color": "black"}
        ),
        dcc.Slider(
            0, frames_cnt-1, 1, value=0, 
            marks={0:'0', 100:'100', 200:'200', 300:'300', 400:'400', (frames_cnt-1):f'{frames_cnt}'}, 
            id='camera-position-slider',
            updatemode='drag'
        ),
        html.Div("Vybraná pozice: 0", id='camera-position-label'),
        html.Div("Zobrazení vrstev:"),
        dcc.Checklist(
            options=[
                {'label': 'záber z kamery', 'value': 'pic'},
                {'label': 'mračno bodů', 'value': 'pcl'}
            ],
            value=['pic', 'pcl'],
            id='layers-checklist'
        ),
        html.Div(
            [
                dash_deck.DeckGL(
                data=deck_dict,
                style={"height": "80vh", 
                    "width": "80vw", 
                    "marginLeft": "0%", 
                    "marginTop": "10.5%"},
                id="point-cloud-visualization"
                ),
            ], style = {
                "backgroundImage": "url(/assets/rails_photo_0.png)",
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

# animation
@callback(
    Output(component_id='camera-position-slider', component_property='value'),
    Output(component_id='point-cloud-visualization', component_property='data'),
    Output(component_id='camera-position-label', component_property='children'),
    Input("animation-interval", "n_intervals"),
)
def shift_camera(n_intervals):
    new_pos = ANIMATION_FRAMES_STEP * n_intervals
    if new_pos >= frames_cnt:
        new_pos = 0    # end of animation, return to the beginning
    
    # change the transformation function in Deck.GL visualization
    patched_dict = Patch()
    patched_dict["layers"][0]["getPosition"] = f"@@=[{transf_strings[new_pos]}]"
    return new_pos, patched_dict, f"Vybraná pozice: {new_pos}"

"""
# shift by slider
@callback(
    Output(component_id='point-cloud-visualization', component_property='data'),
    Output(component_id='camera-position-label', component_property='children'),
    Input(component_id='camera-position-slider', component_property='value'),
    prevent_initial_call=True
)
def shift_camera(new_pos):
    # change the transformation function in Deck.GL visualization
    patched_dict = Patch()
    patched_dict["layers"][0]["getPosition"] = f"@@=[{transf_strings[new_pos]}]"
    return patched_dict, f"Vybraná pozice: {new_pos}"
"""

if __name__ == "__main__":
    app.run(debug=True)
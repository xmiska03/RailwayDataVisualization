import dash
from dash import html, dcc, callback, Output, Input
import dash_deck
import pydeck as pdk
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
FAR = 300                    # far plane
TRANSPARENCY = 90


def load_csv_into_nparray(file_address):
    with open(file_address, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        return np.array(data, dtype=float)
    

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

# a function to change the tranformation of the point cloud quickly
def replace_transformation(pydeck_json, new_transf_string):
    # finds the current point cloud transformation in the JSON representation 
    # of the Pydeck visualization ("getPosition": "@@=[...]") and replaces it 
    # with the new transformation

    search_length = 700        # it should be in the last 700 characters
    search_substring = pydeck_json[-search_length:]

    # find the substring "getPosition": "@@=["
    target = '"getPosition": "@@=['
    start_index = search_substring.find(target)

    if start_index != -1:
        # find the closing bracket
        opening_bracket_index = start_index + len(target)
        closing_bracket_index = search_substring.find(']', opening_bracket_index)

        if closing_bracket_index != -1:
            # replace the transformation
            modified_substring = (
                search_substring[:opening_bracket_index]
                + new_transf_string
                + search_substring[closing_bracket_index:]
            )
            return pydeck_json[:-search_length] + modified_substring

    return pydeck_json


# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

# load data about camera positions (order of the columns: y, z, x)
trans_nparray = load_csv_into_nparray("data/trans.csv")
rot_nparray = load_csv_into_nparray("data/rot.csv")

# number of frames to generate (500 in example data)
frames_cnt = trans_nparray.shape[0]

# calculate the initial transformation matrix
transf_mat = calculate_transformation_matrix(trans_nparray, rot_nparray, 0)

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])


# visualize the point cloud using Pydeck
point_cloud_layer = pdk.Layer(
    "PointCloudLayer",
    data=pc_df,
    get_position=[
        f"x * {transf_mat[0][0]} + y * {transf_mat[0][1]} + z * {transf_mat[0][2]} + {transf_mat[0][3]}", 
        f"x * {transf_mat[1][0]} + y * {transf_mat[1][1]} + z * {transf_mat[1][2]} + {transf_mat[1][3]}", 
        f"x * {transf_mat[2][0]} + y * {transf_mat[2][1]} + z * {transf_mat[2][2]} + {transf_mat[2][3]}"
    ],
    get_color=["intensity > 6 ? 7 * (intensity - 6) : 0",  # 6 is the average
               "intensity > 6 ? 255 - 7 * (intensity - 6) : 51 * (intensity - 6)",
               "intensity > 6 ? 0 : 255 - 51 * (intensity - 6)",
               TRANSPARENCY
    ],
    #get_color=["intensity > 9 ? 255 : 0",
    #           "(intensity > 5 && intensity <= 9) ? 255 : 0",
    #           "intensity <= 5 ? 255 : 0",
    #           125     # alpha
    #],
    get_normal=[0, 0, 0],
    auto_highlight=True,
    pickable=True,
    point_size=POINT_SIZE,
)

view_state = pdk.ViewState(
    target=TARGET,
    rotation_orbit=ROTATION_ORBIT,
    rotation_x=ROTATION_X,
    controller=True,
    zoom=ZOOM
)
view = pdk.View(type="OrbitView", controller=True, fovy=FOVY, far=FAR)

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
        dcc.Slider(
            0, frames_cnt-1, 20, value=0, 
            #marks={0:'0', (frames_cnt-1):f'{frames_cnt}'}, 
            id='camera-position-slider'
        ),
        html.Div("Vybraná pozice: 0", id="camera-position-label"),
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
                data=deck_json,
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
@callback(
    Output(component_id='point-cloud-visualization', component_property='data'),
    Output(component_id='camera-position-label', component_property='children'),
    Input(component_id='camera-position-slider', component_property='value')
)
def shift_camera(new_pos):
    # calculate the new transformation matrix
    transf_mat = calculate_transformation_matrix(trans_nparray, rot_nparray, new_pos)

    new_transf_str = f"x * {transf_mat[0][0]} + y * {transf_mat[0][1]} + z * {transf_mat[0][2]} + {transf_mat[0][3]}, x * {transf_mat[1][0]} + y * {transf_mat[1][1]} + z * {transf_mat[1][2]} + {transf_mat[1][3]}, x * {transf_mat[2][0]} + y * {transf_mat[2][1]} + z * {transf_mat[2][2]} + {transf_mat[2][3]}"

    new_json = replace_transformation(deck_json, new_transf_str)
    return new_json, f"Vybraná pozice: {new_pos}"

if __name__ == "__main__":
    app.run(debug=True)
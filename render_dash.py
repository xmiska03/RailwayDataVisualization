from dash import Dash, html, dcc, callback, Output, Input, State, Patch, ctx, clientside_callback
import dash_deck
import pandas as pd
import numpy as np
from pypcd4 import PointCloud
import csv
from scipy.spatial.transform import Rotation


# visualization parameters
POINT_SIZE = 50
TARGET = [0, -0.3, 1.0]      # move the camera left/right, up/down
ROTATION_ORBIT = 91.8        # turn the camera left/right
ROTATION_X = 4.0             # turn the camera up/down
ZOOM = 10
FOVY = 21                    # focal length
FAR_PLANE = 200
OPACITY = 0.5
ANIMATION_SPEED = 2         # frames per second
ANIMATION_FRAMES_STEP = 10
BACKGROUND_IMAGE = "url(/assets/rails_photo_0.png)"

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

def intensity_to_colors(pc_nparray):
    #"getColor": (
    #    "@@=[intensity > 6 ? 7 * (intensity - 6) : 0, "
    #    "intensity > 6 ? 255 - 7 * (intensity - 6) : 51 * (intensity - 6), "
    #    f"intensity > 6 ? 0 : 255 - 51 * (intensity - 6), 225]"
    #),
    red = np.where(pc_nparray[:, 3] > 6, 7 * (pc_nparray[:, 3] - 6), 0)
    green = np.where(pc_nparray[:, 3] > 6, 255 - 7 * (pc_nparray[:, 3] - 6), 51 * (pc_nparray[:, 3]))
    blue = np.where(pc_nparray[:, 3] > 6, 0, 255 - 51 * (pc_nparray[:, 3]))
    return np.column_stack((pc_nparray[:, :3], red, green, blue))

# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

#pc_nparray = pc_nparray[:20000]

# pre-count colors
pc_nparray = intensity_to_colors(pc_nparray)

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
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "r", "g", "b"])

# prepare the visualization of the point cloud using Deck.GL
point_cloud_layer = {
    "@@type": "PointCloudLayer",
    "data": pc_df.to_dict(orient="records"),
    "getColor": "@@=[r, g, b]",
    "getPosition": f"@@=[{transf_strings[0]}]",
    #"getPosition": f"@@=[x, y, z]",
    "pointSize": POINT_SIZE,
    "opacity": OPACITY,
    "visible": True,
    #"transitions": {
    #    "getPosition": 1000
    #}
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
            max_intervals=frames_cnt/ANIMATION_FRAMES_STEP,
            disabled=True
        ),
        dcc.Store(
            id='current-frame-store',
            data=0
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
        
        html.Button('Přehrát', id='play-button'),
        html.Button('Zastavit', id='stop-button'),
        
        html.Div("Pozice kamery: "),
        dcc.Input(
            "0",
            id="camera-position-input",
            type="number",
            min=0,
            max=frames_cnt-1
        ),
    
        html.Div("Zobrazení vrstev:"),
        dcc.Checklist(
            options=[
                {'label': 'záber z kamery', 'value': 'pic'}
            ],
            value=['pic'],
            id='camera-picture-checkbox'
        ),
        dcc.Checklist(
            options=[
                {'label': 'mračno bodů', 'value': 'pcl'}
            ],
            value=['pcl'],
            id='point-cloud-checkbox'
        ),
        
        html.Div(
            [
                dash_deck.DeckGL(
                data=deck_dict,
                style={"height": "80vh", 
                    "width": "80vw", 
                    "marginLeft": "0%", 
                    "marginTop": "0%"},
                id="point-cloud-visualization"
                ),
            ], 
            id = "pcl-visualization-div",
            style = {
                "backgroundImage": BACKGROUND_IMAGE,
                "backgroundSize": "cover",
                "backgroundRepeat": "no-repeat",
                "backgroundPosition": "center",
                "height": "80vh",
                "width": "80vw",
                "margin": "0",
                "padding": "0",
                "position": "relative" 
            }
        )
    ],
    style={
        "height": "100vh",
        "width": "80vw",
        "margin": "0",
        "padding": "0",
        "fontSize": "14px"
    },
)


# callbacks - the logic of the app

# change frame by the input field, slider or as a part of the animation
@callback(
    Output('current-frame-store', 'data'),
    Output('camera-position-input', 'value'),
    Output('camera-position-slider', 'value'),
    Input('camera-position-input', 'value'),
    Input('camera-position-slider', 'value'),
    Input("animation-interval", "n_intervals"),
    prevent_initial_call=True
)
def change_frame(input_val, slider_val, interval_val):
    triggered_id = ctx.triggered_id
    if triggered_id == 'camera-position-input':   # frame changed by input field
        if isinstance(input_val, int):
            return input_val, input_val, input_val
        else:
            return slider_val, input_val, slider_val
    
    elif triggered_id == 'camera-position-slider':   # frame changed by slider
        return slider_val, slider_val, slider_val
    
    elif triggered_id == 'animation-interval':   # frame changed as a part of the animation
        new_pos = ANIMATION_FRAMES_STEP * interval_val
        if new_pos >= frames_cnt:
            new_pos = 0    # end of animation, return to the beginning
        return new_pos, new_pos, new_pos

# play/pause the animation
@callback(
    Output('animation-interval', 'n_intervals'),
    Output('animation-interval', 'disabled'),
    State('current-frame-store', 'data'),
    Input('play-button', 'n_clicks'),
    Input('stop-button', 'n_clicks'),
    prevent_initial_call=True
)
def control_animation(curr_pos, btn1, btn2):
    triggered_id = ctx.triggered_id
    if triggered_id == 'play-button':
        # start animation from the current position
        return int(curr_pos/ANIMATION_FRAMES_STEP)+1, False
    if triggered_id == 'stop-button':
        # stop animation
        return int(curr_pos/ANIMATION_FRAMES_STEP), True

# turn the background image on/off
@callback(
    Output('pcl-visualization-div', 'style'),
    Input('camera-picture-checkbox', 'value'),
)
def change_background(layers):
    patched_style = Patch()
    if 'pic' in layers:
        patched_style["backgroundImage"] = BACKGROUND_IMAGE
    else:
        patched_style["backgroundImage"] = "none"
    return patched_style

# react to changed frame number or point cloud layer visibility
@callback(
    Output('point-cloud-visualization', 'data'),
    Input('current-frame-store', 'data'),
    Input('point-cloud-checkbox', 'value'),
    prevent_initial_call=True
)
def change_point_cloud(new_pos, layers):
    patched_data = Patch()

    triggered_id = ctx.triggered_id
    if triggered_id == 'current-frame-store':
        # change the transformation function in Deck.GL visualization
        patched_data["layers"][0]["getPosition"] = f"@@=[{transf_strings[new_pos]}]"
        #patched_data["initialViewState"]["target"] = [0.5*new_pos, -0.3, 1.0]
    
    elif triggered_id == 'point-cloud-checkbox':
        # change the visibility of point cloud layer
        if 'pcl' in layers:
            patched_data["layers"][0]["visible"] = True
        else:
            patched_data["layers"][0]["visible"] = False
        
    return patched_data

if __name__ == "__main__":
    app.run(debug=True)
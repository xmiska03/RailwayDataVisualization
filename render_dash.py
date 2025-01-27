from dash import Dash, html, dcc, callback, Output, Input, State, Patch, ctx, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from pypcd4 import PointCloud
import csv
from scipy.spatial.transform import Rotation


# visualization parameters
POINT_SIZE = 16
POSITION = [0, -1.1, 0.45]      # move the camera left/right, up/down
BEARING = 91.5          # turn the camera left/right
PITCH = 1.3             # turn the camera up/down
ZOOM = 10
FOVY = 37                    # focal length
FAR_PLANE = 300
OPACITY = 0.7
ANIMATION_SPEED = 6          # frames per second
ANIMATION_FRAMES_STEP = 2
LINE_WIDTH = 60

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

# creates a JSON-like array of lines from a numpy array of points representing a polyline
def create_lines_data(points_nparray):
    lines = []
    for i in range(len(points_nparray) - 1):
        line = {
            "from": {"x": points_nparray[i, 0], "y": points_nparray[i, 1], "z": points_nparray[i, 2]},
            "to": {"x": points_nparray[i+1, 0], "y": points_nparray[i+1, 1], "z": points_nparray[i+1, 2]}
        }
        lines.append(line)
    return lines

# load point cloud
pc = PointCloud.from_path("data/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

#pc_nparray = pc_nparray[::10]

# load vector data (lines)
lines1 = create_lines_data(load_csv_into_nparray("data/polyline1.csv"))
lines2 = create_lines_data(load_csv_into_nparray("data/polyline2.csv"))
lines3 = create_lines_data(load_csv_into_nparray("data/polyline3.csv"))
lines_data = lines1 + lines2 + lines3

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
    #"@@type": "PointCloudLayer",
    "data": pc_df.to_dict(orient="records"),
    #"getColor": "@@=[intensity*6, intensity*6, intensity*6]",
    #"getPosition": f"@@=[{transf_strings[0]}]",
    "pointSize": POINT_SIZE,
    "pointColor": 'rgb',
    "opacity": OPACITY,
    "visible": True,
    #"transitions": {
    #    "getPosition": 1000
    #}
}

line_layer = {
    "data": lines_data,
    "color": [250, 100, 15],
    "width": LINE_WIDTH,
    "visible": True
}

view_state = {
    "bearing": BEARING,
    "pitch": PITCH,
    "position": POSITION,
    "zoom": ZOOM
}

view = {
    #"@@type": "OrbitView",
    "far": FAR_PLANE,
    "fovy": FOVY,
    "controller": True
}

deck_dict = {
    "initialViewState": view_state,
    "views": [view],
    "layers": [point_cloud_layer, line_layer],
}

# create a Dash app
app = Dash(
    __name__,
    title = "Vizualizace dat z MMS",
    update_title = "Načítání...",
    external_stylesheets = [dbc.themes.FLATLY, "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"]
)

down_panel = [
    dbc.Col(dbc.Button(html.I(className="bi bi-play-fill"), id='play-button'), width=1),
    dbc.Col(dcc.Slider(
        0, frames_cnt-1, 1, value=0, 
        marks={0:'0', 100:'100', 200:'200', 300:'300', 400:'400', (frames_cnt-1):f'{frames_cnt}'}, 
        id='camera-position-slider',
        updatemode='drag'
    ), width=10)
]

camera_position_widget = [
    dbc.Col(html.Div("Pozice kamery: "), width=5),
    dbc.Col(dbc.Input(
        value="0",
        id="camera-position-input",
        type="number",
        min=0,
        max=frames_cnt-1
    ), width=7)
]

point_size_widget = [
    dbc.Col(html.Div("Velikost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{POINT_SIZE}",
        id="point-size-input",
        type="number",
        min=1,
        max=50
    ), width=7)
]

point_color_widget = [
    dbc.Col(html.Div("Barevná škála: "), width=5),
    dbc.Col(dcc.Dropdown(
        options={'rgb': 'rudo-zeleno-modrá', 'rb': 'rudo-modrá', 'yr': 'žluto-rudá'},
        value='rgb',
        clearable=False,
        id='point-color-dropdown'
    ), width=7)
]

point_opacity_widget = [
    dbc.Col(html.Div("Průhlednost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{OPACITY}",
        id="point-opacity-input",
        type="number",
        min=0,
        max=1,
        step=0.1
    ), width=7)
]

right_panel = [
    dbc.Row(camera_position_widget),
    dbc.Row(html.Div("Zobrazení vrstev:")),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' záběr z kamery', 'value': 'pic'}],
            value=['pic'],
            id='camera-picture-checkbox'
        )
    ),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' mračno bodů', 'value': 'pcl'}],
            value=['pcl'],
            id='point-cloud-checkbox'
        )
    ),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' vektorová data', 'value': 'vec'}],
            value=['vec'],
            id='vector-data-checkbox'
        )
    ),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_size_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_color_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_opacity_widget)
]

visualization = html.Div(
    [
        html.Video(
            src="/assets/new_video_compatible.mp4",
            id="background-video",
            style={'width': '100%', 'height': 'auto', "display": "block"}
        ),
        #html.Img(
        #    src="/assets/video_frames/0.jpg",
        #    id="background-img",
        #    style={'width': '100%', 'height': 'auto', "display": "block"}
        #),
        html.Canvas(
            id='visualization-canvas',
            style={
                'position': 'absolute',
                'top': 0,
                'left': 0
            }
        ),
        dcc.Store(
            id='visualization-data',
            data=deck_dict
        ),
        dcc.Store(
            id='visualization-change',
        )
    ],
    style = {
        "position": "relative" 
    }
)

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
        dcc.Store(
            id='animation-running-store',
            data=False
        ),

        html.H4(
            "Vizualizace dat z mobilního mapovacího systému",
            style={"textAlign": "center", "padding":"10px"}
        ),
        dbc.Row(
            [
                dbc.Col([
                    visualization,
                    dbc.Placeholder(color="black"),
                    dbc.Row(down_panel, justify="center", align="end")    
                ], width=6),
                dbc.Col(right_panel, width=3)
            ],
            justify="center"
        ),
        html.Div(id="dummy"),  # because the initializing callback needs some output
    ],
    style={
        "fontSize": "16px"
    },
)


# callbacks - the logic of the app
"""
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
    Output('play-button', 'children'),
    Output('animation-running-store', 'data'),
    State('current-frame-store', 'data'),
    Input('play-button', 'n_clicks'),
    State('animation-running-store', 'data'),
    prevent_initial_call=True
)
def control_animation(curr_pos, btn, animation_running):
    triggered_id = ctx.triggered_id
    if triggered_id == 'play-button':
        # start animation from the current position
        if animation_running:
            # pause
            return int(curr_pos/ANIMATION_FRAMES_STEP), True, html.I(className="bi bi-play-fill"), False
        else:
            # play
            return int(curr_pos/ANIMATION_FRAMES_STEP)+1, False, html.I(className="bi bi-pause-fill"), True
"""

"""
# change the background image (or turn it off/on)
@callback(
    Output('background-img', 'src'),
    Output('background-img', 'style'),
    Input('current-frame-store', 'data'),
    Input('camera-picture-checkbox', 'value'),
)
def change_background(new_pos, layers):
    patched_style = Patch()
    if 'pic' in layers:
        patched_style["visibility"] = "visible"
    else:
        patched_style["visibility"] = "hidden"
    return f"/assets/video_frames/{new_pos}.jpg", patched_style
"""

# turn the background video on/off
@callback(
    Output('background-video', 'style'),
    Input('camera-picture-checkbox', 'value'),
)
def change_background(options_list):
    patched_style = Patch()
    if 'pic' in options_list:
        patched_style["visibility"] = "visible"
    else:
        patched_style["visibility"] = "hidden"
    return patched_style

# play video and animation
app.clientside_callback(
    """
    function(btn) {
        window.runDeckAnimation();
        
        const video = document.getElementById('background-video');
        video.play();
    }
    """,
    Input("play-button", "n_clicks"),
    prevent_initial_call=True
)
    
# initialize the point cloud
app.clientside_callback(
    """
    function(data_dict) {
        if (window.initializeDeck) {
            console.log("Calling initializeDeck");
            window.data_dict = data_dict;  // initialize the global variables
            window.position = 0;
            window.initializeDeck();  // call function defined in the JavaScript file
        }
        return 'dummy';
    }
    """,
    Output('dummy', 'id'),  # needed for the initial call
    Input('visualization-data', 'data')
)

"""
# shift the point cloud
app.clientside_callback(
    
    function(position) {
        if (window.updatePosition) {
            window.position = position;
            window.updatePosition();  // call function defined in the JavaScript file
        }
    }
    ,
    Input('current-frame-store', 'data'),
    prevent_initial_call=True
)
"""

# change point cloud visibility, point size, color scale or opacity
app.clientside_callback(
    """
    function(layers, point_size, color_scale, opacity) {  
            if (window.updatePCLayerProps) {
            // call function defined in the JavaScript file
            window.updatePCLayerProps(layers.includes('pcl'), point_size, color_scale, opacity);
        }
    }
    """,
    Input('point-cloud-checkbox', 'value'),
    Input('point-size-input', 'value'),  # Dash sometimes gives number inputs as strings, sometimes as numbers!
    Input('point-color-dropdown', 'value'),
    Input('point-opacity-input', 'value'),
    prevent_initial_call=True
)

# change vector data visibility
app.clientside_callback(
    """
    function(layers) {
        if (window.updateLineLayerProps) {
            // call function defined in the JavaScript file
            window.updateLineLayerProps(layers.includes('vec'));
        }
    }
    """,
    Input('vector-data-checkbox', 'value'),
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run(debug=True)
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

# pre-calculate all transformation matrices
transf_matrices = []
for i in range(frames_cnt):
    transf_matrix = calculate_transformation_matrix(trans_nparray, rot_nparray, i)
    transf_matrices.append(transf_matrix)

# create a pandas DataFrame
pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])

# prepare the visualization of the point cloud using Deck.GL
point_cloud_layer = {
    "data": pc_df.to_dict(orient="records"),
    "pointSize": POINT_SIZE,
    "pointColor": 'rgb',
    "opacity": OPACITY,
    "visible": True
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
    "far": FAR_PLANE,
    "fovy": FOVY,
    "controller": False
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

down_panel_upper = [
    dbc.Col(dbc.Button(html.I(className="bi bi-play-fill"), id='play-button'), width=1),
    dbc.Col(html.Div("00:00", id="current-time-div"), width=1),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-position-slider-input",
        type="range",
        min=0,
        max=frames_cnt-1,
        style={'width': '100%'}
    ), width=9),
    dbc.Col(html.Div("00:19", id="total-time-div"), width=1),
]

down_panel_lower = [
    html.Div("Snímek:"),
    dbc.Input(
        value="0",
        id="camera-position-input",
        type="number",
        min=0,
        max=frames_cnt-1,
        style={'width':'90px'}
    ),
    html.Div(
        "",
        className="ms-auto",   # works as a spacer
    ),
    html.Div("Rychlost:"),
    dcc.Dropdown(
        options={'2': '2×', '1': '1×', '0.5': '0.5×'},
        value='1',
        clearable=False,
        id='animation-speed-dropdown',
        style={'width':'80px'}
    )
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
    dbc.Row(dbc.Placeholder(color="white"),),
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
            id='translations-data',
            data=trans_nparray
        ),
        dcc.Store(
            id='rotations-data',
            data=rot_nparray
        ),
        dcc.Store(
            id='transformations-data',
            data=transf_matrices
        ),
    ],
    style = {
        "position": "relative" 
    }
)

app.layout = html.Div(children=
    [
        dbc.Placeholder(color="white"),
        dbc.Row(
            [
                dbc.Col([
                    visualization,
                    dbc.Placeholder(color="white"),
                    dbc.Row(down_panel_upper, justify="center", align="start"),
                    dbc.Stack(
                        down_panel_lower,
                        direction="horizontal",
                        gap=3,
                    ),
                ], width=6),
                dbc.Col(dbc.Tabs(
                    [
                        dbc.Tab(right_panel, tab_id="vis", label="Zobrazení", label_style={"padding": "10px"}),
                        dbc.Tab("", tab_id="data", label="Data", label_style={"padding": "10px"}),
                        dbc.Tab("", tab_id="prof", label="Průjezdný profil", label_style={"padding": "10px"}),
                    ],
                    active_tab="vis"
                ), width=3)
            ],
            justify="center"
        )
    ],
    style={
        "fontSize": "16px"
    },
)


# callbacks - the logic of the app

# initialize the point cloud
app.clientside_callback(
    """
    function(data_dict) {
        if (window.initializeDeck) {
            window.data_dict = data_dict;  // initialize the global variables
            window.position = 0;
            window.initializeDeck();  // call function defined in the JavaScript file
        }
        return dash_clientside.no_update;
    }
    """,
    Output('visualization-data', 'id'),  # dummy output needed so that the initial call occurs
    Input('visualization-data', 'data')
)

# initialize the transformations data
app.clientside_callback(
    """
    function(transf_data) {
        if (window.initializeDeck) {
            window.transf = transf_data;  // make the data accessible for the visualization.js script
        }
        return dash_clientside.no_update;
    }
    """,
    Output('transformations-data', 'id'),  # dummy output needed so that the initial call occurs
    Input('transformations-data', 'data')
)

# play/pause the animation
# this function handles the video, deck.gl visualization and play button icon
app.clientside_callback(
    """
    function(btn) {
        const video = document.getElementById('background-video');
        const icon = document.getElementById("play-button").querySelector("i"); 
        
        if (!window.animation_running) {
            window.runDeckAnimation();         // run both deck animation and the video
            video.play();
        } else {
            window.stopDeckAnimation();
            video.pause();
            // TODO: fix possible offset
            //window.position = Math.floor(video.currentTime * 25);
            //window.updatePosition();
        }

        icon.classList.toggle("bi-play-fill");    // change icon
        icon.classList.toggle("bi-pause-fill");

    }
    """,
    Input("play-button", "n_clicks"),
    prevent_initial_call=True
)

# change the frame by number input or slider
app.clientside_callback(
    """
    function(input_val, slider_val_dec) {
        if (!isNaN(input_val)) {
            const slider_val = Math.floor(parseFloat(slider_val_dec));
            
            // get the new position - which one triggered the callback, slider or input?
            const triggered_id = dash_clientside.callback_context.triggered_id;
            const new_pos = (triggered_id == 'camera-position-input') ? parseInt(input_val) : slider_val;
            
            if (new_pos != window.position) {
                // update deck.gl visualization
                window.position = new_pos;
                window.updatePosition();  // call function defined in the JavaScript file
                
                // update video
                const video = document.getElementById('background-video');
                const videoTime = new_pos / 25;
                video.currentTime = videoTime;

                // update slider and input field and time label
                dash_clientside.set_props("camera-position-slider-input", {value: new_pos});
                dash_clientside.set_props("camera-position-input", {value: new_pos});

                // update time label
                const time_sec = Math.floor(videoTime);
                const minutes = Math.floor(time_sec / 60);
                const seconds = time_sec % 60;
                const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
                dash_clientside.set_props("current-time-div", {children: label});
            }
        }
    }
    """,
    Input('camera-position-input', 'value'),
    Input('camera-position-slider-input', 'value'),
    prevent_initial_call=True
)

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
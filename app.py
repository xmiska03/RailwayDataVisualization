from dash import Dash, html, dcc, callback, Output, Input, State, Patch, ctx, clientside_callback
import dash_bootstrap_components as dbc
from pypcd4 import PointCloud
from scipy.spatial.transform import Rotation

import data_tab_components
import data_tab_callbacks
import visualization_tab_components
import visualization_tab_callbacks
import gauge_tab_components
import gauge_tab_callbacks
import animation_control_components
import animation_control_callbacks
import params
from general_functions import load_csv_into_nparray, load_yaml_into_dict, calculate_projection_matrix, \
                              calculate_translation_from_extr_mat, load_timestamps_into_nparray


# load point cloud
pc = PointCloud.from_path("data/joined/scans.pcd")
pc_nparray = pc.numpy(("x", "y", "z", "intensity"))

#pc_nparray = pc_nparray[::10]   # reduce the size of the point cloud

# load camera parameters
camera_params_dict = load_yaml_into_dict("data/camera_azd.yaml")
distortion_coeffs = camera_params_dict['DistCoeffs']['data']
#calibration_matrix = load_csv_into_nparray("data/joined/K.csv")
proj_matrix = calculate_projection_matrix(camera_params_dict)
camera_translation = calculate_translation_from_extr_mat(camera_params_dict)

# load data about camera positions
# load translations
trans_nparray = load_csv_into_nparray("data/joined/trans_joined.csv")
# fix the order of columns in the translations array: yzx -> xyz
trans_nparray = trans_nparray[:, [2, 0, 1]]
# load rotations
rot_nparray_raw = load_csv_into_nparray("data/joined/rot_joined.csv")
rot_nparray = []
rot_inv_nparray = []
bearing_pitch_array = []
for rotation_xzy in rot_nparray_raw:
    # if translations are in order yzx instead of xyz, then rotations are in order xzy instead of zyx
    rotation = Rotation.from_euler("xzy", rotation_xzy, degrees=True)
    rotation_zyx = rotation.inv().as_euler("zyx", degrees=True)
    bearing_pitch_array.append([-rotation_zyx[0], rotation_zyx[1]])  # only bearing (z) and pitch (y)
    rot_nparray.append(rotation.as_matrix())
    rot_inv_nparray.append(rotation.inv().as_matrix())
# load timestamps
timestamps_nparray = load_timestamps_into_nparray("data/joined/imu_joined_timestamps.csv")
# convert timestamps so that they start from 0 and are in seconds
timestamp0 = int(timestamps_nparray[0])
timestamps_nparray = (timestamps_nparray - timestamp0) / 1000000000  # nanoseconds to seconds

# number of frames to generate
frames_cnt = trans_nparray.shape[0]

# load vector data (polylines)
paths_data = [
    #load_csv_into_nparray("data/polyline1.csv"),
    #load_csv_into_nparray("data/polyline2.csv"),
    #load_csv_into_nparray("data/polyline3.csv")
]

# load loading gauge data
gauge_data = [load_csv_into_nparray("data/loading_gauge.csv")]

# prepare the visualization of the point cloud using Deck.GL
point_cloud_layer = {
    "data": pc_nparray,
    "pointSize": params.POINT_SIZE,
    "pointColor": 'bgr',
    "opacity": params.OPACITY,
    "visible": True
}

path_layer = {
    "data": paths_data,
    "color": [250, 100, 15],    # #fa650f
    "width": params.LINE_WIDTH,
    "visible": True
}

loading_gauge_layer = {
    "data": gauge_data,
    "color": [225, 80, 255],    # #e250ff
    "width": params.GAUGE_LINE_WIDTH,
    "visible": True
}

view_state = {
    "bearing": params.BEARING,
    "pitch": params.PITCH,
    "position": [params.POSITION_OFFSET[0], params.POSITION_OFFSET[1], params.POSITION_OFFSET[2]]
    #[camera_translation[0] + params.POSITION_OFFSET[0],
    #camera_translation[1] + params.POSITION_OFFSET[1],
    #camera_translation[2] + params.POSITION_OFFSET[2]]
}

view = {
    "projectionMatrix": proj_matrix,
    "controller": True
}

deck_dict = {
    "initialViewState": view_state,
    "views": [view],
    "layers": [point_cloud_layer, path_layer, loading_gauge_layer],
}

# a part of the Dash app which visualizes the data
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
        html.Canvas(
            id='distorted-visualization-canvas',
            style={
                'position': 'absolute',
                'top': 0,
                'left': 0
            }
        )
    ],
    style = {
        "position": "relative" 
    }
)

# the left side of the screen with the visualization and animation controls 
app_left_col = dbc.Col(
    [
        visualization,
        dbc.Placeholder(color="white"),
        dbc.Row(
            animation_control_components.down_panel_upper, 
            justify="center",
            align="start"
        ),
        dbc.Stack(
            animation_control_components.down_panel_lower,
            direction="horizontal",
            gap=3
        ),
    ], width=6
)
    
# the right side of the screen with tabs
app_right_col = dbc.Col(  
    dbc.Tabs(
        [
            dbc.Tab(
                visualization_tab_components.visualization_tab,
                tab_id="vis",
                label="Zobrazení",
                label_style={"padding": "10px"},
                style={"height": "70vh", "overflowY": "auto", "overflowX":"hidden"}
            ),
            dbc.Tab(
                data_tab_components.data_tab, 
                tab_id="data", 
                label="Data", 
                label_style={"padding": "10px"}
            ),
            dbc.Tab(
                gauge_tab_components.gauge_tab, 
                tab_id="gauge", 
                label="Průjezdný profil", 
                label_style={"padding": "10px"}
            )
        ],
        active_tab="vis"
    ), style={}, width=4
)

# stores used for storing data on the clients side
stores = [
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
        id='rotations-inv-data',
        data=rot_inv_nparray
    ),
    dcc.Store(
        id='gauge-transf-data'
    ),
    dcc.Store(
        id='bearing-pitch-data',   # special rotations for deck.gl 
        data=bearing_pitch_array
    ),
    dcc.Store(
        id='camera-timestamps-data',
        data=timestamps_nparray
    )
] 


# create a Dash app
app = Dash(
    __name__,
    title = "Vizualizace dat z MMS",
    update_title = "Načítání...",
    external_stylesheets = [
        dbc.themes.BOOTSTRAP, 
        "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"
    ]
)

app.server.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB to allow a longer video

# Dash app layout
app.layout = html.Div(
    [
        dbc.Placeholder(color="white"),
        dbc.Row(
            [
                app_left_col,
                app_right_col
            ],
            justify="center"
        ),
        dbc.Row(stores)
    ],
    style={
        "fontSize": "16px"
    },
)


# callbacks - the logic of the app

# (re)initialize the deck visualization
app.clientside_callback(
    """
    function(data_dict, camera_timestamps) {
        if (window.initializeDeck) {
            window.data_dict = data_dict;  // make the data accessible to visualizations.js
            window.camera_timestamps = camera_timestamps;
            window.initializeDeck();       // call function defined in the JavaScript file
        }
        return dash_clientside.no_update;
    }
    """,
    Output('visualization-data', 'id'),  # dummy output needed so that the initial call occurs
    Input('visualization-data', 'data'),
    Input('camera-timestamps-data', 'data')
)

# add callbacks defined in other files
visualization_tab_callbacks.get_callbacks(app)
data_tab_callbacks.get_callbacks(app)
gauge_tab_callbacks.get_callbacks(app)
animation_control_callbacks.get_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
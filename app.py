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
from general_functions import calculate_projection_matrix, calculate_translation_from_extr_mat, \
                              load_rotation, rotation_to_euler, rotation_to_matrix, rotation_to_inv_matrix
from loading_functions import load_csv_file_into_nparray, load_yaml_into_dict, \
                              load_timestamps_file_into_nparray, load_space_separated_into_nparray, \
                                load_pcl_timestamps


# load unaggregated point cloud data
pc_nparray = []
for i in range(596):
    pc = PointCloud.from_path(f"data/joined/joined_pcd_files/pcd_{i}.pcd")
    pc_nparray.append(pc.numpy(("x", "y", "z", "intensity")))

# load unaggregated point cloud timestamps
pcl_timestamps = load_pcl_timestamps("data/joined/joined_pcl_timestamps.txt")

# load aggregated point cloud data
#united_pc = PointCloud.from_path("data/joined/scans.pcd")
united_pc = PointCloud.from_path("data/joined/joined_pcd_files/pcd_0.pcd")   # for development
united_pc_nparray = united_pc.numpy(("x", "y", "z", "intensity"))

# load camera parameters
camera_params_dict = load_yaml_into_dict("data/camera_azd.yaml")
distortion_coeffs = camera_params_dict['DistCoeffs']['data']
#calibration_matrix = load_csv_file_into_nparray("data/joined/K.csv")
proj_matrix = calculate_projection_matrix(camera_params_dict)
camera_translation = calculate_translation_from_extr_mat(camera_params_dict)

# load data about camera positions
# load translations and fix the order of columns in the translations array: yzx -> xyz
trans_nparray = load_csv_file_into_nparray("data/joined/trans_joined.csv")[:, [2, 0, 1]]
# load rotations
rot_nparray_raw = load_csv_file_into_nparray("data/joined/rot_joined.csv")
rot_nparray = []
rot_inv_nparray = []
rot_euler_array = []
for rot_raw in rot_nparray_raw:
    rotation = load_rotation(rot_raw)
    rot_euler_array.append(rotation_to_euler(rotation))
    rot_nparray.append(rotation_to_matrix(rotation))
    rot_inv_nparray.append(rotation_to_inv_matrix(rotation))
# load timestamps
timestamps_nparray = load_timestamps_file_into_nparray("data/joined/imu_joined_timestamps.csv")

# number of frames to generate
frames_cnt = trans_nparray.shape[0]

# load loading gauge data
gauge_data = [load_csv_file_into_nparray("data/loading_gauge.csv")]
# load predicted translations in distances 25m, 50m, 75m, 100m
gauge_translations = [
    load_space_separated_into_nparray("data/joined/profile/profile_trans_25.csv")[:, [2, 0, 1]],
    load_space_separated_into_nparray("data/joined/profile/profile_trans_50.csv")[:, [2, 0, 1]],
    load_space_separated_into_nparray("data/joined/profile/profile_trans_75.csv")[:, [2, 0, 1]],
    load_space_separated_into_nparray("data/joined/profile/profile_trans_100.csv")[:, [2, 0, 1]]
]
# load predicted rotations in distances 25m, 50m, 75m, 100m
gauge_rotations_inv = [[] for _ in range(4)]
for i in range(4):
    gauge_rotations_raw = load_space_separated_into_nparray(f"data/joined/profile/profile_rot_{25 + i*25}.csv")
    for rotation_xzy in rot_nparray_raw:
        # if translations are in order yzx instead of xyz, then rotations are in order xzy instead of zyx
        rotation = Rotation.from_euler("xzy", rotation_xzy, degrees=True)
        gauge_rotations_inv[i].append(rotation.inv().as_matrix())

# load vector data (polylines)
paths_data = [
    # for now only the loading gauge line is here
    [gauge_translations[0]],
    [gauge_translations[1]],
    [gauge_translations[2]],
    [gauge_translations[3]]
    #load_csv_file_into_nparray("data/polyline1.csv"),
    #load_csv_file_into_nparray("data/polyline2.csv"),
    #load_csv_file_into_nparray("data/polyline3.csv")
]

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
    "color": [232, 175, 16],    # #e8af10
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
}

view = {
    "projectionMatrix": proj_matrix,
    "controller": False
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
            src="/assets/video_long_compatible.mp4",
            id="background-video",
            style={
                'height': '100%',
                'display': 'block'
            }
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
        'height': '100%',
        'aspectRatio': '2048/1536',
        'margin': 'auto',
        'position': 'relative',
        'overflow': 'hidden'
    }
)
    
# the right side of the screen with tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(
            dcc.Loading(        # display a circle over the data tab when the app is loading something
                type="circle",
                overlay_style={"visibility":"visible"},
                children=data_tab_components.data_tab
            ),
            tab_id="data", 
            label="Data", 
            label_style={"padding": "10px"},
            style={"height": "calc(100vh - 100px)", "overflowY": "auto", "overflowX":"hidden"}
        ),
        dbc.Tab(
            visualization_tab_components.visualization_tab,
            tab_id="vis",
            label="Zobrazení",
            label_style={"padding": "10px"},
            style={"height": "calc(100vh - 100px)", "overflowY": "auto", "overflowX":"hidden"}
        ),
        dbc.Tab(
            gauge_tab_components.gauge_tab, 
            tab_id="gauge", 
            label="Průjezdný profil", 
            label_style={"padding": "10px"}
        )
    ],
    active_tab="data"
)

# the right margin of the page, almost empty, contains only a color mode switch
color_mode_switch = html.Div(
    [
        html.I(className="bi bi-moon"),
        dbc.Switch(
            id="color-mode-switch",
            value=False,
            className="d-inline-block ms-1",
            persistence=True,
            style={"marginRight": "-3px"}),
        html.I(className="bi bi-sun")
    ],
    id = 'color-mode-div',
    style={
        'position': 'fixed', 
        'top': 0, 
        'right': 0,
        'backgroundColor': '#212529',
        'opacity': 0.95,
        'borderRadius': 30,
        'padding': '10px 15px',
        'fontSize': '1.1rem'
    }
)


# stores used for storing data on the clients side
stores = [
    dcc.Store(
        id='visualization-data',
        data=deck_dict
    ),
    dcc.Store(
        id='united-pc-data',
        data=united_pc_nparray
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
        id='rotations-euler-data',
        data=rot_euler_array
    ),
    
    dcc.Store(
        id='gauge-trans-data',         # for the loading gauge (train profile)
        data=gauge_translations
    ),
    dcc.Store(
        id='gauge-rot-inv-data',
        data=gauge_rotations_inv
    ),
    dcc.Store(
        id='gauge-transf-data'
    ),
    
    dcc.Store(
        id='camera-timestamps-data',
        data=timestamps_nparray
    ),
    dcc.Store(
        id='pcl-timestamps-data',
        data=pcl_timestamps
    ),

    dcc.Store(
        id='display-united-store',  # decides whether the app displays united point cloud data or not
        data=False
    )
] 

main_part = [    # visualization + animation controls, takes full screen
    visualization,
    color_mode_switch,
    animation_control_components.bottom_panel,
]

side_panel = [ 
    html.Div(
        tabs,
        style={
            'overflow': 'hidden',
            'padding': '10px 0 20px 12px',
            'height': '100vh',
        }
    ),
    dbc.Button(
        html.I(className="bi bi-list"),
        id="roll-out-button",
        style={
            'position': 'absolute', 
            'top': 0, 
            'left': '100%',
            'backgroundColor': '#212529',
            'opacity': 0.95,
            'borderRadius': 30,
            'border': '1px solid white',
            'fontSize': '1.8rem',
            'padding': '2px 15px'
        }
    )
]

app_layout = [
    html.Div(
        side_panel,
        id='side-panel-div', 
        style={
            'width': 0,    # hidden at the beginning
            'boxSizing': 'border-box',
            'transition': 'width 0.5s',
            'height': '100vh',
            'position': 'relative',
            'zIndex': 1,
            'flexShrink': 0
        }
    ),
    html.Div(main_part, style={'height': '100vh', 'flexGrow': 1, 'position': 'relative'}),
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

app.server.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB to allow a longer video

# Dash app layout
app.layout = html.Div(
    [
        html.Div(stores),
        html.Div(
            app_layout,
            style={
                'width': '98vw',
                'fontSize': '16px',
                'display': 'flex'
            }
        )
    ]
)


# callbacks - the logic of the app

# (re)initialize the deck visualization
app.clientside_callback(
    """
    function(data_dict, united_pc_data, camera_timestamps, pcl_timestamps) {
        if (window.initializeDeck) {
            window.data_dict = data_dict;  // make the data accessible to visualizations.js
            window.united_pc_data = united_pc_data;
            window.pcl_timestamps = pcl_timestamps;
            window.camera_timestamps = camera_timestamps;
            window.initializeDeck();       // call function defined in the JavaScript file
        }
        return dash_clientside.no_update;
    }
    """,
    Output('visualization-data', 'id'),  # dummy output needed so that the initial call occurs
    Input('visualization-data', 'data'),
    Input('united-pc-data', 'data'),
    Input('camera-timestamps-data', 'data'),
    State('pcl-timestamps-data', 'data')
)

# roll out the side panel on button click
app.clientside_callback(
    """
    function(n_clicks) {
        const side_panel = document.getElementById('side-panel-div');
        const bottom_panel = document.getElementById('bottom-panel-div');
        const icon = document.getElementById("roll-out-button").querySelector("i");
        
        if (n_clicks % 2 == 1) {
            // roll out side panel
            bottom_panel.style.width = 'calc(100% - 500px)';
            side_panel.style.width = '500px';
            // change the icon
            icon.classList.remove("bi-list");
            icon.classList.add("bi-caret-left");
        } else {
            // pack side panel
            bottom_panel.style.width = '100%'
            side_panel.style.width = 0;
            // change the icon
            icon.classList.add("bi-list");
            icon.classList.remove("bi-caret-left");
        }
    }
    """,
    Input("roll-out-button", "n_clicks")
)

# change color mode by switch
app.clientside_callback(
    """
    function(switch_on) {
        let color = '';
        let opposite_color = '';

        if (switch_on) {
            // light mode
            color = 'white';
            opposite_color = '#212529';
            document.documentElement.setAttribute('data-bs-theme', 'light');
        } else {
            // dark mode
            color = '#212529';
            opposite_color = 'white'
            document.documentElement.setAttribute('data-bs-theme', 'dark');
        }

        document.getElementById("roll-out-button").style.backgroundColor = color;
        document.getElementById("roll-out-button").style.borderColor = opposite_color;
        document.getElementById("roll-out-button").querySelector("i").style.color = opposite_color;      
        document.getElementById("color-mode-div").style.backgroundColor = color;
        document.getElementById("camera-position-div").style.backgroundColor = color;
        document.getElementById("play-controls-div").style.backgroundColor = color;
        document.getElementById("play-button").querySelector("i").style.color = opposite_color;  
        return dash_clientside.no_update;
    }
    """,
    Output("color-mode-switch", "id"),  # dummy output needed so that the initial call occurs
    Input("color-mode-switch", "value"),
)

# add callbacks defined in other files
visualization_tab_callbacks.get_callbacks(app)
data_tab_callbacks.get_callbacks(app)
gauge_tab_callbacks.get_callbacks(app)
animation_control_callbacks.get_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
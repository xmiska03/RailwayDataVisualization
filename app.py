from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from pypcd4 import PointCloud
import os

import layout_components
import data_tab_callbacks
import visualization_tab_callbacks
import profile_tab_callbacks
import animation_control_callbacks
import layout_callbacks
import params
from general_functions import calculate_projection_matrix, calculate_translation_from_extr_mat, \
                              load_rotation, rotation_to_euler, rotation_to_matrix, rotation_to_inv_matrix
from loading_functions import load_csv_file_into_nparray, load_yaml_into_dict, \
                              load_timestamps_file_into_nparray, \
                              load_pcl_timestamps, load_profile_translations, load_profile_rotations


# create directory for temporary files
if not os.path.exists("assets/temp"):
   os.makedirs("assets/temp")

# load unaggregated point cloud data
pc_nparray = []
for i in range(596):
    pc = PointCloud.from_path(f"data/joined/joined_pcd_files/pcd_{i}.pcd")
    pc_nparray.append(pc.numpy(("x", "y", "z", "intensity")))
    #pc_nparray.append(pc.numpy(("x", "y", "z", "intensity"))[:1])    # for testing
    #points = np.vstack((pc.numpy(("x", "y", "z", "intensity"))))    # for testing 
    #pc_nparray.append(points[:1000])
    

# load unaggregated point cloud timestamps
pcl_timestamps = load_pcl_timestamps("data/joined/joined_pcl_timestamps.txt")
#pcl_timestamps = [i * 0.04 for i in range(596)]   # for testing 

# load aggregated point cloud data
#united_pc = PointCloud.from_path("data/joined/scans.pcd")
united_pc = PointCloud.from_path("data/joined/joined_pcd_files/pcd_0.pcd")   # for development
united_pc_nparray = united_pc.numpy(("x", "y", "z", "intensity"))
#united_pc_nparray = np.vstack((united_pc_nparray, united_pc_nparray))    # for testing 
#united_pc_nparray = united_pc_nparray[:8000000]    # for testing 
#print(len(united_pc_nparray))

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
#timestamps_nparray = pcl_timestamps    # for testing 

# number of frames to generate
frames_cnt = trans_nparray.shape[0]

# load train profile data
profile_shape = [load_csv_file_into_nparray("data/train_profile_shape.csv")]
profile_translations = load_profile_translations("data/joined/profile", "profile_trans")
profile_rotations = load_profile_rotations("data/joined/profile", "profile_rot")
profile_line_data = [[profile_translations[0]], [profile_translations[1]], [profile_translations[2]],
                    [profile_translations[3]]]

# load vector data (polylines)
vector_data = [
    load_csv_file_into_nparray("data/vector_data/polyline2.csv"),
    load_csv_file_into_nparray("data/vector_data/polyline3.csv")
]

# prepare the visualization of the point cloud using Deck.GL

point_cloud_layer = {
    "data": pc_nparray,
    "pointSize": params.POINT_SIZE,
    "pointColor": 'bgr',
    "opacity": params.OPACITY,
    "visible": True
}

profile_line_layer = {
    "data": [],   # data for this layer is in the profile-line-data store
    "color": [232, 175, 16],    # #e8af10
    "width": params.LINE_WIDTH,
    "visible": True
}

profile_layer = {
    "data": profile_shape,
    "color": [225, 80, 255],    # #e250ff
    "width": params.PROFILE_LINE_WIDTH,
    "visible": True
}

vector_layer = {
    "data": [],   # data for this layer is in the vector-data store
    "color": [250, 101, 15],    # #fa650f
    "width": params.LINE_WIDTH,
    "visible": True
}

view = {
    "projectionMatrix": proj_matrix,
    "controller": False
}

deck_dict = {
    "views": [view],
    "layers": [point_cloud_layer, profile_line_layer, profile_layer, vector_layer],
}

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
        id='pcl-timestamps-data',
        data=pcl_timestamps
    ),

    dcc.Store(
        id='profile-line-data',
        data=profile_line_data
    ),
    dcc.Store(
        id='vector-data',
        data=vector_data
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
        id='camera-timestamps-data',
        data=timestamps_nparray
    ),
    
    dcc.Store(
        id='profile-trans-data',         # for the train profile
        data=profile_translations
    ),
    dcc.Store(
        id='profile-rot-data',
        data=profile_rotations
    ),
    dcc.Store(
        id='profile-transf-data'
    ),

    dcc.Store(
        id='point-cloud-type-store',  # decides whether the app displays united or divided point cloud data
        data='divided'
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

app.server.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB to allow a longer video

# Dash app layout
app.layout = html.Div(
    [
        html.Div(stores),
        html.Div(
            layout_components.app_layout,
            style={
                'width': '100vw',
                'fontSize': '16px',
                'display': 'flex'
            }
        )
    ]
)


# callbacks - the logic of the app

# initialize the deck visualization
app.clientside_callback(
    """
    function(data_dict, united_pc_data, pcl_timestamps, profile_line_data, vector_data, 
             translations, rotations, rotations_inv, rotations_euler, camera_timestamps) {
        if (window.vis) {
            window.vis.data_dict = data_dict;  // make the data accessible to visualization.js
            window.vis.united_pc_data = united_pc_data;
            window.vis.pcl_timestamps = pcl_timestamps;
            window.vis.profile_line_data = profile_line_data;
            window.vis.vector_data = vector_data;
            
            window.vis.translations = translations;
            window.vis.rotations = rotations;
            window.vis.rotations_inv = rotations_inv;
            window.vis.rotations_euler = rotations_euler;
            window.vis.camera_timestamps = camera_timestamps;
            window.vis.initializeDeck();       // call function defined in the JavaScript file
        }

        // disable picture-in-picture in mozilla
        const video = document.getElementById('background-video');
        video.disablePictureInPicture = true;

        return dash_clientside.no_update;
    }
    """,
    Output('visualization-data', 'id'),  # dummy output needed so that the initial call occurs
    Input('visualization-data', 'data'),
    State('united-pc-data', 'data'),
    State('pcl-timestamps-data', 'data'),
    State('profile-line-data', 'data'),
    State('vector-data', 'data'),
    State('translations-data', 'data'),
    State('rotations-data', 'data'),
    State('rotations-inv-data', 'data'),
    State('rotations-euler-data', 'data'),
    State('camera-timestamps-data', 'data'),
    
)

# add callbacks defined in other files
visualization_tab_callbacks.get_callbacks(app)
data_tab_callbacks.get_callbacks(app)
profile_tab_callbacks.get_callbacks(app)
animation_control_callbacks.get_callbacks(app)
layout_callbacks.get_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
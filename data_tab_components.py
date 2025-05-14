## @file data_tab_components.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash components used in the "data" tab.

from dash import html, dcc
import dash_bootstrap_components as dbc

from params import FAR_PLANE


## @brief The style for the uploading boxes.
upload_box_style = {
    'width': '95%',
    'height': '40px',
    'lineHeight': '40px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '10px',
    'textAlign': 'center',
    'margin': '10px',
    'cursor': 'pointer',
    'boxShadow': '0px 2px 5px rgba(0, 0, 0, 0.1)'
}

## @brief The style for the deleting buttons ("x" buttons).
delete_button_style = {
    'background': 'none',
    'border': 'none',
    'color': 'inherit',
    'padding': '0'
}

## @brief The structure of the uploading boxes for single files.
upload_structure = html.Div([    # icon + text on upload widget
    html.I(className="bi bi-upload", style={'margin': '5px'}),
    'Vybrat soubor'
])

## @brief The structure of the uploading boxes for multiple files.
upload_multiple_structure = html.Div([    # icon + text on upload widget
    html.I(className="bi bi-upload", style={'margin': '5px'}),
    'Vybrat soubory'
])

## @brief A component used for spacing in components displaying uploaded files.
spacer = html.Div("", className="ms-auto")

## @brief The icon "x" for the deleting buttons.
icon_x = html.I(className="bi bi-x-lg")



## @brief A widget for uploading a project file.
project_file_upload = dcc.Upload(id='project-file-upload', children=upload_structure, 
                                 style=upload_box_style)
## @brief A widget for uploading postprocess point cloud.
united_pc_upload = dcc.Upload(id='united-pc-upload', children=upload_structure, 
                              style=upload_box_style)
## @brief A widget for uploading real-time point cloud.
divided_pc_upload = dcc.Upload(id='divided-pc-upload', children=upload_multiple_structure, 
                              style=upload_box_style, multiple=True)
## @brief A widget for uploading point cloud timestamps.
pc_timestamps_upload = dcc.Upload(id='pc-timestamps-upload', children=upload_structure, 
                                  style=upload_box_style)
## @brief A widget for uploading camera translations.
translations_upload = dcc.Upload(id='translations-upload', children=upload_structure, 
                                 style=upload_box_style)
## @brief A widget for uploading camera rotations.
rotations_upload = dcc.Upload(id='rotations-upload', children=upload_structure, 
                              style=upload_box_style)
## @brief A widget for uploading camera timestamps.
timestamps_upload = dcc.Upload(id='timestamps-upload', children=upload_structure, 
                               style=upload_box_style)
## @brief A widget for uploading a video.
video_upload = dcc.Upload(id='video-upload', children=upload_structure, 
                          style=upload_box_style)
## @brief A widget for uploading vector data.
vector_data_upload = dcc.Upload(id='vector-data-upload', children=upload_multiple_structure, 
                                style=upload_box_style, multiple=True)
## @brief A widget for uploading train profile translations.
profile_trans_upload = dcc.Upload(id='profile-trans-upload', children=upload_multiple_structure, 
                                  style=upload_box_style, multiple=True)
## @brief A widget for uploading train profile rotations.
profile_rot_upload = dcc.Upload(id='profile-rot-upload', children=upload_multiple_structure, 
                                style=upload_box_style, multiple=True)


## @brief A widget which displays the uploaded project file.
project_file_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-text"),
        html.Div("", id="project-file-filename-div"),
        spacer,
        dbc.Button(icon_x, id='project-file-delete-button', style=delete_button_style),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded postprocess point cloud file.
united_pc_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-binary"),
        html.Div("", id="united-pc-filename-div"),
        spacer,
        dbc.Button(icon_x, id='united-pc-delete-button', style=delete_button_style),
        # a special store used to trigger a clienside callback to update the point cloud visualization
        dcc.Store(id="update-pcd-store", data=0),
        dcc.Store(id="united-pcd-path-store", data="")  # for a file path set by the project file
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded real-time point cloud files.
divided_pc_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-files"),
        html.Div("", id="divided-pc-filename-div"),
        spacer,
        dbc.Button(icon_x, id='divided-pc-delete-button', style=delete_button_style),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix", "files_cnt"
        dcc.Store(id="divided-pcd-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded point cloud timestamps file.
pc_timestamps_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-txt"),
        html.Div("", id="pc-timestamps-filename-div"),
        spacer,
        dbc.Button(icon_x, id='pc-timestamps-delete-button', style=delete_button_style),
        dcc.Store(id="pc-timestamps-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded video file.
video_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-mp4"),
        html.Div("", id="video-filename-div"),
        spacer,
        dbc.Button(icon_x, id='video-delete-button', style=delete_button_style),
        # a special store used to trigger a clienside callback to update the video time
        dcc.Store(id="update-video-store", data=0),
        dcc.Store(id="video-path-store", data=""),
        # an interval to delete temporary video files created when users upload new videos
        dcc.Interval(
            id="delete-temp-video-interval",
            interval=120000,  # 2 minutes
        ),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded postprocess vector data file.
vector_data_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-files"),
        html.Div("", id="vector-data-filename-div"),
        spacer,
        dbc.Button(icon_x, id='vector-data-delete-button', style=delete_button_style),
        dcc.Store(id="vector-data-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded camera translations file.
translations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="translations-filename-div"),
        spacer,
        dbc.Button(icon_x, id='translations-delete-button', style=delete_button_style),
        dcc.Store(id="translations-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded camera rotations file.
rotations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="rotations-filename-div"),
        spacer,
        dbc.Button(icon_x, id='rotations-delete-button', style=delete_button_style),
        dcc.Store(id="rotations-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded camera timestamps file.
timestamps_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="timestamps-filename-div"),
        spacer,
        dbc.Button(icon_x, id='timestamps-delete-button', style=delete_button_style),
        dcc.Store(id="timestamps-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded train profile translations file.
profile_trans_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-files"),
        html.Div("", id="profile-trans-filename-div"),
        spacer,
        dbc.Button(icon_x, id='profile-trans-delete-button', style=delete_button_style),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix"
        dcc.Store(id="profile-trans-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which displays the uploaded train profile rotations file.
profile_rot_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-files"),
        html.Div("", id="profile-rot-filename-div"),
        spacer,
        dbc.Button(icon_x, id='profile-rot-delete-button', style=delete_button_style),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix"
        dcc.Store(id="profile-rot-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

## @brief A widget which allow to set the far plane.
far_plane_widget = [
    dbc.Col(html.Div("Maximální vzdálenost (m): "), width=5),
    dbc.Col(dbc.Input(
        value=f"{FAR_PLANE}",
        id="far-plane-input",
        type="number",
        min=1,
        max=500,
        step=1
    ), width=6)
]

## @brief The whole content of the "data" tab.
data_tab = [
    # project file
    dbc.Row(html.Div("Projektový soubor (.toml)"), style={"fontWeight": "bold", "textAlign": "center", "marginTop": "25px"}),
    dbc.Row(html.Div(project_file_upload, id="project-file-upload-div")),
    dbc.Row(html.Div(project_file_uploaded_file, id="project-file-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'20px'})),

    # point cloud
    dbc.Row(html.Div("Mračno bodů"), style={"fontWeight": "bold", "textAlign": "center"}), 
    # united point cloud
    dbc.Row(html.Div("Mračno bodů typu postprocess (.pcd):")),
    dbc.Row(html.Div(united_pc_upload, id="united-pc-upload-div")),
    dbc.Row(html.Div(united_pc_uploaded_file, id="united-pc-uploaded-file-div")),
    # divided point cloud (+ timestamps) is "read-only" in the GUI, can only be changed in the project file
    dbc.Row(html.Div("Mračno bodů typu real-time (.pcd soubory):")),
    dbc.Row(html.Div(divided_pc_upload, id="divided-pc-upload-div")),
    dbc.Row(html.Div(divided_pc_uploaded_files, id="divided-pc-uploaded-file-div")),
    dbc.Tooltip(
        "Při nahrávání mimo projektový soubor musí být tyto soubory pojmenovány 'pcd_0.pcd', 'pcd_1.pcd', atd.",
        target="divided-pc-upload-div",
    ),
    dbc.Row(html.Div("Časová razítka mračna bodů typu real-time (.txt):")),
    dbc.Row(html.Div(pc_timestamps_upload, id="pc-timestamps-upload-div")),
    dbc.Row(html.Div(pc_timestamps_uploaded_file, id="pc-timestamps-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),
    
    # video
    dbc.Row(html.Div("Video (.mp4, kódování H.264)"), style={"fontWeight": "bold", "textAlign": "center"}), 
    dbc.Row(html.Div(video_upload, id="video-upload-div")),
    dbc.Row(html.Div(video_uploaded_file, id="video-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),

    # vector data
    dbc.Row(html.Div("Vektorová data (.csv soubory)"), style={"fontWeight": "bold", "textAlign": "center"}),
    dbc.Row(html.Div(vector_data_upload, id="vector-data-upload-div")),
    dbc.Row(html.Div(vector_data_uploaded_files, id="vector-data-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),

    # the virtual camera
    dbc.Row(html.Div("Virtuální kamera"), style={"fontWeight": "bold", "textAlign": "center"}), 
    dbc.Row(html.Div("Translace (.csv):")),
    dbc.Row(html.Div(translations_upload, id="translations-upload-div")),
    dbc.Row(html.Div(translations_uploaded_file, id="translations-uploaded-file-div")),
    dbc.Row(html.Div("Rotace (.csv):")),
    dbc.Row(html.Div(rotations_upload, id="rotations-upload-div")),
    dbc.Row(html.Div(rotations_uploaded_file, id="rotations-uploaded-file-div")),
    dbc.Row(html.Div("Časová razítka pozic (.csv):")),
    dbc.Row(html.Div(timestamps_upload, id="timestamps-upload-div")),
    dbc.Row(html.Div(timestamps_uploaded_file, id="timestamps-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),

    # the profile
    dbc.Row(html.Div("Průjezdný profil"), style={"fontWeight": "bold", "textAlign": "center"}), 
    dbc.Row(html.Div("Translace (.csv soubory):")),
    dbc.Row(html.Div(profile_trans_upload, id="profile-trans-upload-div")),
    dbc.Row(html.Div(profile_trans_uploaded_files, id="profile-trans-uploaded-file-div")),
    dbc.Tooltip(
        "Při nahrávání mimo projektový soubor musí mít názvy těchto souborů koncovky '25.csv', '50.csv', '75.csv' a '100.csv'.",
        target="profile-trans-upload-div",
    ),
    dbc.Row(html.Div("Rotace (.csv soubory):")),
    dbc.Row(html.Div(profile_rot_upload, id="profile-rot-upload-div")),
    dbc.Row(html.Div(profile_rot_uploaded_files, id="profile-rot-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),
    dbc.Tooltip(
        "Při nahrávání mimo projektový soubor musí mít názvy těchto souborů koncovky '25.csv', '50.csv', '75.csv' a '100.csv'.",
        target="profile-rot-upload-div",
    ),

    dbc.Row(html.Div("Parametry kamery"), style={"fontWeight": "bold", "textAlign": "center"}), 
    dbc.Row(html.Div("Kalibrační matice:")),
    dbc.Row(dcc.Textarea(
        value="2437.045995, 0, 1030.357277,\n0, 2442.940956, 729.596405,\n0, 0, 1",
        id="calibration-matrix-textarea",
        style={'margin': '10px 16px', 'width': '90%', 'height': '85px'}
    )),
    dbc.Row(far_plane_widget, style={'marginTop': '15px'}),
    dcc.Store(id="projection-matrix-store"),
    dbc.Row(
        html.Div([
            "Parametry zkreslení (k", html.Sub("1"), ", ", "k", html.Sub("2"), ", ",
            "p", html.Sub("1"), ", ", "p", html.Sub("2"), ", ", "k", html.Sub("3"), "):"
        ]),
        style={'marginTop': '10px'}
    ),
    dbc.Row(dcc.Textarea(
        value="-0.183217, 0.026917, -0.001191, 0.000804, 0.335446",
        id="distortion-params-textarea",
        style={'margin': '10px 16px', 'width': '90%', 'height': '40px'}
    )),
    dcc.Store(id="distortion-params-store", data=[-0.183217, 0.026917, -0.001191, 0.000804, 0.335446]),
]


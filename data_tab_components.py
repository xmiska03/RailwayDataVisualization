# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc


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

uploaded_file_box_style = {
    'background': 'none',
    'border': 'none',
    'color': 'inherit',
    'padding': '0'
}

# some components
upload_design = html.Div([    # icon + text on upload widget
    html.I(className="bi bi-upload", style={'margin': '5px'}),
    'Vybrat soubor'
])
spacer = html.Div("", className="ms-auto")
icon_x = html.I(className="bi bi-x-lg")

# widgets for uploading files
project_file_upload = dcc.Upload(id='project-file-upload', children=upload_design, style=upload_box_style)
united_pc_upload = dcc.Upload(id='united-pc-upload', children=upload_design, style=upload_box_style)
translations_upload = dcc.Upload(id='translations-upload', children=upload_design, style=upload_box_style)
rotations_upload = dcc.Upload(id='rotations-upload', children=upload_design, style=upload_box_style)
timestamps_upload = dcc.Upload(id='timestamps-upload', children=upload_design, style=upload_box_style)
video_upload = dcc.Upload(id='video-upload', children=upload_design, style=upload_box_style)

# widgets which display uploaded files

project_file_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-text"),
        html.Div("", id="project-file-filename-div"),
        spacer,
        dbc.Button(icon_x, id='project-file-delete-button', style=uploaded_file_box_style),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

united_pc_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-binary"),
        html.Div("", id="united-pc-filename-div"),
        spacer,
        dbc.Button(icon_x, id='united-pc-delete-button', style=uploaded_file_box_style),
        # a special store used to trigger a clienside callback to update the point cloud visualization
        dcc.Store(id="update-pcd-store", data=0),
        dcc.Store(id="united-pcd-path-store", data="")  # for a file path set by the project file
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

divided_pc_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-binary"),
        html.Div("", id="divided-pc-filename-div"),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix", "files_cnt"
        dcc.Store(id="divided-pcd-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

pc_timestamps_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-filetype-txt"),
        html.Div("", id="pc-timestamps-filename-div"),
        dcc.Store(id="pc-timestamps-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)


video_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-mp4"),
        html.Div("", id="video-filename-div"),
        spacer,
        dbc.Button(icon_x, id='video-delete-button', style=uploaded_file_box_style),
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


vector_data_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="vector-data-filename-div"),
        dcc.Store(id="vector-data-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)


translations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="translations-filename-div"),
        spacer,
        dbc.Button(icon_x, id='translations-delete-button', style=uploaded_file_box_style),
        dcc.Store(id="translations-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

rotations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="rotations-filename-div"),
        spacer,
        dbc.Button(icon_x, id='rotations-delete-button', style=uploaded_file_box_style),
        dcc.Store(id="rotations-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

timestamps_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="timestamps-filename-div"),
        spacer,
        dbc.Button(icon_x, id='timestamps-delete-button', style=uploaded_file_box_style),
        dcc.Store(id="timestamps-path-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

profile_trans_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="profile-trans-filename-div"),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix"
        dcc.Store(id="profile-trans-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

profile_rot_uploaded_files = dbc.Stack(
    [
        html.I(className="bi bi-filetype-csv"),
        html.Div("", id="profile-rot-filename-div"),
        # this store will be set by the project file and it will be a dictionary with these keys:
        # "dir_path", "filename_prefix"
        dcc.Store(id="profile-rot-paths-store", data="")
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)



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
    dbc.Row(html.Div(divided_pc_uploaded_files, id="divided-pc-uploaded-file-div")),
    dbc.Row(html.Div("Časová razítka mračna bodů typu real-time (.txt):")),
    dbc.Row(html.Div(pc_timestamps_uploaded_files, id="pc-timestamps-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),
    
    # video
    dbc.Row(html.Div("Video (.mp4)"), style={"fontWeight": "bold", "textAlign": "center"}), 
    dbc.Row(html.Div(video_upload, id="video-upload-div")),
    dbc.Row(html.Div(video_uploaded_file, id="video-uploaded-file-div")),
    dbc.Row(html.Hr(style={'marginTop':'15px'})),

    # vector data
    dbc.Row(html.Div("Vektorová data (.csv soubory)"), style={"fontWeight": "bold", "textAlign": "center"}),
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
    dbc.Row(html.Div(profile_trans_uploaded_files, id="profile-trans-uploaded-file-div")),
    dbc.Row(html.Div("Rotace (.csv soubory):")),
    dbc.Row(html.Div(profile_rot_uploaded_files, id="profile-rot-uploaded-file-div")),

]


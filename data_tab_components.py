# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc


upload_box_style = {
    'width': '100%',
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

upload_design = html.Div([
    html.I(className="bi bi-upload", style={'margin':'5px'}),
    'Vybrat soubor'
])

point_cloud_upload = dcc.Upload(
    id='point-cloud-upload',
    children=upload_design,
    style=upload_box_style
)

translations_upload = dcc.Upload(
    id='translations-upload',
    children=upload_design,
    style=upload_box_style
)

rotations_upload = dcc.Upload(
    id='rotations-upload',
    children=upload_design,
    style=upload_box_style
)

video_upload = dcc.Upload(
    id='video-upload',
    children=upload_design,
    style=upload_box_style
)

point_cloud_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-binary"),
        html.Div("", id="point-cloud-filename-div"),
        html.Div(
            "",
            className="ms-auto",   # works as a spacer
        ),
        dbc.Button(
            html.I(className="bi bi-x-lg"),
            id='point-cloud-delete-button', 
            style={"background": "none", "border": "none", "color": "inherit", "padding": "0"}
        ),
        # a special store used to trigger a clienside callback to update the point cloud visualization
        dcc.Store(id="update-pcd-store", data=0)
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

translations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-text"),
        html.Div("", id="translations-filename-div"),
        html.Div(
            "",
            className="ms-auto",   # works as a spacer
        ),
        dbc.Button(
            html.I(className="bi bi-x-lg"),
            id='translations-delete-button', 
            style={"background": "none", "border": "none", "color": "inherit", "padding": "0"}
        ),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

rotations_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-text"),
        html.Div("", id="rotations-filename-div"),
        html.Div(
            "",
            className="ms-auto",   # works as a spacer
        ),
        dbc.Button(
            html.I(className="bi bi-x-lg"),
            id='rotations-delete-button', 
            style={"background": "none", "border": "none", "color": "inherit", "padding": "0"}
        ),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

video_uploaded_file = dbc.Stack(
    [
        html.I(className="bi bi-file-earmark-play"),
        html.Div("", id="video-filename-div"),
        html.Div(
            "",
            className="ms-auto",   # works as a spacer
        ),
        dbc.Button(
            html.I(className="bi bi-x-lg"),
            id='video-delete-button', 
            style={"background": "none", "border": "none", "color": "inherit", "padding": "0"}
        ),
        # a special store used to trigger a clienside callback to update the video time
        dcc.Store(id="update-video-store", data=0),
        # an interval to delete temporary video files created when users upload new videos
        dcc.Interval(
            id="delete-temp-video-interval",
            interval=120000,  # 2 minutes
        ),
    ], direction="horizontal", gap=2, style={'margin': '10px'}
)

data_tab = [
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat spojené mračno bodů', 'value': 'united'}],
            value=[],
            id='display-united-checkbox',
            style={'marginTop':'20px', 'marginBottom':'20px'}
        )
    ),
    dbc.Row(html.Div("Spojené mračno bodů:")),
    dbc.Row(html.Div(point_cloud_upload, id="point-cloud-upload-div")),
    dbc.Row(html.Div(point_cloud_uploaded_file, id="point-cloud-uploaded-file-div")),
    dbc.Row(html.Div("Translace:")),
    dbc.Row(html.Div(translations_upload, id="translations-upload-div")),
    dbc.Row(html.Div(translations_uploaded_file, id="translations-uploaded-file-div")),
    dbc.Row(html.Div("Rotace:")),
    dbc.Row(html.Div(rotations_upload, id="rotations-upload-div")),
    dbc.Row(html.Div(rotations_uploaded_file, id="rotations-uploaded-file-div")),
    dbc.Row(html.Div("Video:")),
    dbc.Row(html.Div(video_upload, id="video-upload-div")),
    dbc.Row(html.Div(video_uploaded_file, id="video-uploaded-file-div"))
]


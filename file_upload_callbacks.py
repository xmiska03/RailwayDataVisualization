# This file contains definitions of dash callbacks used in the "data" tab of the app.

from dash import Output, Input, State
import base64


def get_callbacks(app):
    # upload/delete file with point cloud
    @app.callback(
        Output('point-cloud-upload-div', 'style'),
        Output('point-cloud-uploaded-file-div', 'style'),
        Output('point-cloud-filename-div', 'children'),
        Input('point-cloud-upload', 'contents'),
        State('point-cloud-upload', 'filename')
    )
    def upload_point_cloud(file_content, filename):
        if file_content is not None:
            # new file uploaded
            #content_type, content_string = file_content.split(',')
            #decoded = base64.b64decode(content_string)
            #print(decoded)
            return {"display": "none"}, {"display": "block"}, filename
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, ""

    # upload/delete file with translations
    @app.callback(
        Output('translations-upload-div', 'style'),
        Output('translations-uploaded-file-div', 'style'),
        Output('translations-filename-div', 'children'),
        Input('translations-upload', 'contents'),
        State('translations-upload', 'filename')
    )
    def upload_translations(file_content, filename):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)
            #print("uploaded translations: ", decoded)
            return {"display": "none"}, {"display": "block"}, filename
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, ""

    # react to uploaded/deleted file with rotations
    @app.callback(
        Output('rotations-upload-div', 'style'),
        Output('rotations-uploaded-file-div', 'style'),
        Output('rotations-filename-div', 'children'),
        Input('rotations-upload', 'contents'),
        State('rotations-upload', 'filename')
    )
    def upload_rotations(file_content, filename):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)
            #print("uploaded rotations: ", decoded)
            return {"display": "none"}, {"display": "block"}, filename
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, ""

    # upload/delete file with video
    @app.callback(
        Output('video-upload-div', 'style'),
        Output('video-uploaded-file-div', 'style'),
        Output('video-filename-div', 'children'),
        Input('video-upload', 'contents'),
        State('video-upload', 'filename')
    )
    def upload_video(file_content, filename):
        if file_content is not None:
            # new file uploaded
            #content_type, content_string = file_content.split(',')
            #decoded = base64.b64decode(content_string)
            #print(decoded)
            return {"display": "none"}, {"display": "block"}, filename
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, ""
    
    
    # delete file with point cloud
    @app.callback(
        Output('point-cloud-upload', 'contents'),
        Input('point-cloud-delete-button', 'n_clicks')
    )
    def delete_point_cloud(btn):
        return None

    # delete file with translations
    @app.callback(
        Output('translations-upload', 'contents'),
        Input('translations-delete-button', 'n_clicks')
    )
    def delete_translations(btn):
        return None

    # delete file with rotations
    @app.callback(
        Output('rotations-upload', 'contents'),
        Input('rotations-delete-button', 'n_clicks')
    )
    def delete_rotations(btn):
        return None

    # delete file with video
    @app.callback(
        Output('video-upload', 'contents'),
        Input('video-delete-button', 'n_clicks')
    )
    def delete_video(btn):
        return None


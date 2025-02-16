# This file contains definitions of dash callbacks used in the "data" tab of the app.

from dash import Output, Input, State
import base64
import numpy as np

from general_functions import calculate_transformation_matrix


def get_callbacks(app):

    # copy the transformations data from a store to the window object
    app.clientside_callback(
        """
        function(transf_data) {
            window.transf = transf_data;  // make the data accessible for the visualization.js script
            return dash_clientside.no_update;
        }
        """,
        Output('transformations-data', 'id'),  # dummy output needed so that the initial call occurs
        Input('transformations-data', 'data')
    )
    
    # calculate new transformations when new translations or rotations are uploaded
    @app.callback(
        Output('transformations-data', 'data'),  # dummy output needed so that the initial call occurs
        Input('translations-data', 'data'),
        Input('rotations-data', 'data')
    )
    def create_transformations(trans_data, rot_data):
        trans_nparray = np.array(trans_data)  # convert from lists to numpy arrays
        rot_nparray = np.array(rot_data)

        transf_matrices = []
        for i in range(min(trans_nparray.shape[0], rot_nparray.shape[0])):
            transf_matrix = calculate_transformation_matrix(trans_nparray[i], rot_nparray[i])
            transf_matrices.append(transf_matrix)
        return transf_matrices

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

